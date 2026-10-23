"""Secure storage and authentication for locked items, mirroring Vault.swift.

Locked items live in one file encrypted with AES-256-GCM. The key is derived from a ClipBar
password with scrypt and is never written anywhere: a wrong password simply fails to decrypt,
so there is nothing to bypass. After a successful unlock the key stays in memory for a short
grace period, like Touch ID on the Mac, and is then forgotten.
"""

from __future__ import annotations
import base64
import json
import os
import secrets
import threading
import time
from hashlib import scrypt
from pathlib import Path
from typing import Dict, Optional

from clipbar.settings import get_data_dir

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False


class Vault:
    """Encrypted store for locked items, unlocked with the user's ClipBar password."""

    GRACE_PERIOD = 30.0  # seconds
    MIN_PASSWORD = 6
    VERSION = 1
    # scrypt cost: about 0.1 s and 32 MB per guess.
    _N, _R, _P = 2 ** 15, 8, 1
    _AAD = b"clipbar-vault-v1"

    _key: Optional[bytes] = None
    _salt: Optional[bytes] = None
    _secrets: Optional[Dict[str, str]] = None
    _unlocked_until: float = 0.0

    # MARK: - File

    @classmethod
    def _path(cls) -> Path:
        return get_data_dir() / "vault.enc"

    @classmethod
    def is_set_up(cls) -> bool:
        return cls._load_envelope() is not None

    @classmethod
    def _load_envelope(cls) -> Optional[dict]:
        path = cls._path()
        if not path.exists():
            return None
        try:
            env = json.loads(path.read_text("utf-8"))
            if env.get("v") == cls.VERSION:
                return env
        except Exception:
            pass
        # Not a vault this version can open (an older, insecure format): set it aside, never use it.
        try:
            path.replace(path.with_name("vault.enc.unreadable"))
        except Exception:
            pass
        return None

    @classmethod
    def _derive(cls, password: str, salt: bytes) -> bytes:
        return scrypt(password.encode("utf-8"), salt=salt, n=cls._N, r=cls._R, p=cls._P,
                      maxmem=64 * 1024 * 1024, dklen=32)

    @classmethod
    def _persist(cls) -> bool:
        if cls._key is None or cls._salt is None or cls._secrets is None:
            return False
        nonce = secrets.token_bytes(12)
        data = AESGCM(cls._key).encrypt(nonce, json.dumps(cls._secrets).encode("utf-8"), cls._AAD)
        env = {
            "v": cls.VERSION, "kdf": "scrypt", "n": cls._N, "r": cls._R, "p": cls._P,
            "salt": base64.b64encode(cls._salt).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "data": base64.b64encode(data).decode(),
        }
        path = cls._path()
        temp = path.with_suffix(".tmp")
        try:
            fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(env, f)
            temp.replace(path)
            return True
        except Exception:
            try:
                temp.unlink()
            except Exception:
                pass
            return False

    # MARK: - Locking

    @classmethod
    def is_unlocked(cls) -> bool:
        if cls._key is not None and time.time() < cls._unlocked_until:
            return True
        cls.lock()
        return False

    @classmethod
    def lock(cls) -> None:
        cls._key = None
        cls._salt = None
        cls._secrets = None
        cls._unlocked_until = 0.0

    @classmethod
    def _start_grace(cls) -> None:
        cls._unlocked_until = time.time() + cls.GRACE_PERIOD
        try:
            from clipbar.qt import QApplication, QTimer
            # Forget the key once the grace period is over, not just on the next access.
            if QApplication.instance() is not None:
                QTimer.singleShot(int(cls.GRACE_PERIOD * 1000) + 100, cls.is_unlocked)
        except Exception:
            pass

    @classmethod
    def create(cls, password: str) -> bool:
        """Sets the password for a new, empty vault."""
        if not _CRYPTO_AVAILABLE or len(password) < cls.MIN_PASSWORD or cls.is_set_up():
            return False
        cls._salt = secrets.token_bytes(16)
        cls._key = cls._derive(password, cls._salt)
        cls._secrets = {}
        if not cls._persist():
            cls.lock()
            return False
        cls._start_grace()
        return True

    @classmethod
    def unlock(cls, password: str) -> bool:
        """Opens the vault; False for a wrong password or a damaged file."""
        env = cls._load_envelope()
        if not _CRYPTO_AVAILABLE or env is None:
            return False
        try:
            salt = base64.b64decode(env["salt"])
            nonce = base64.b64decode(env["nonce"])
            data = base64.b64decode(env["data"])
            key = cls._derive(password, salt)
            plain = AESGCM(key).decrypt(nonce, data, cls._AAD)
            store = json.loads(plain.decode("utf-8"))
        except (InvalidTag, KeyError, ValueError):
            return False
        cls._key, cls._salt, cls._secrets = key, salt, dict(store)
        cls._start_grace()
        return True

    @classmethod
    def authenticate(cls, reason: str = "use a locked item", parent_widget=None) -> bool:
        """Asks for the ClipBar password unless it was entered in the last 30 seconds."""
        if cls.is_unlocked():
            return True
        # A dialog can only run on the GUI thread; anywhere else the answer is no.
        if threading.current_thread() is not threading.main_thread() or not _CRYPTO_AVAILABLE:
            return False
        try:
            from clipbar.qt import QApplication
            if QApplication.instance() is None:
                return False
            return _PasswordDialog(reason, creating=not cls.is_set_up(), parent=parent_widget).run()
        except Exception:
            return False

    # MARK: - Secrets

    @classmethod
    def read(cls, item_id: str) -> Optional[str]:
        if not cls.is_unlocked():
            return None
        return cls._secrets.get(str(item_id))

    @classmethod
    def write(cls, text: str, item_id: str) -> bool:
        if not cls.authenticate("lock this item"):
            return False
        cls._secrets[str(item_id)] = text
        return cls._persist()

    @classmethod
    def delete(cls, item_id: str) -> bool:
        """Removes a secret. Without a vault there's nothing to remove."""
        if not cls.is_set_up():
            return True
        if not cls.authenticate("unlock this item"):
            return False
        cls._secrets.pop(str(item_id), None)
        return cls._persist()


class _PasswordDialog:
    """The unlock prompt; on first use it sets the ClipBar password instead."""

    def __init__(self, reason: str, creating: bool, parent=None) -> None:
        from clipbar.qt import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, Qt

        self.creating = creating
        self.dialog = d = QDialog(parent)
        d.setWindowTitle("ClipBar")
        d.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        d.setMinimumWidth(360)

        layout = QVBoxLayout(d)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        if creating:
            text = (f"Choose a ClipBar password to {reason}.\n"
                    "Locked items are encrypted with it. If you forget it, they can't be recovered.")
        else:
            text = f"Enter your ClipBar password to {reason}."
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Password")
        layout.addWidget(self.password)

        self.confirm = None
        if creating:
            self.confirm = QLineEdit()
            self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm.setPlaceholderText("Confirm password")
            layout.addWidget(self.confirm)

        self.error = QLabel("")
        self.error.setStyleSheet("color: #ff6b6b;")
        self.error.hide()
        layout.addWidget(self.error)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(d.reject)
        buttons.addWidget(cancel)
        ok = QPushButton("Set Password" if creating else "Unlock")
        ok.setDefault(True)
        ok.clicked.connect(self._submit)
        buttons.addWidget(ok)
        layout.addLayout(buttons)

    def _fail(self, message: str) -> None:
        self.error.setText(message)
        self.error.show()
        self.password.clear()
        if self.confirm is not None:
            self.confirm.clear()
        self.password.setFocus()

    def _submit(self) -> None:
        pw = self.password.text()
        if self.creating:
            if len(pw) < Vault.MIN_PASSWORD:
                return self._fail(f"Use at least {Vault.MIN_PASSWORD} characters.")
            if pw != self.confirm.text():
                return self._fail("The passwords don't match.")
            if Vault.create(pw):
                return self.dialog.accept()
            return self._fail("Couldn't create the vault.")
        if Vault.unlock(pw):
            return self.dialog.accept()
        self._fail("Wrong password.")

    def run(self) -> bool:
        from clipbar.qt import QDialog
        self.dialog.raise_()
        self.dialog.activateWindow()
        return self.dialog.exec() == QDialog.DialogCode.Accepted
