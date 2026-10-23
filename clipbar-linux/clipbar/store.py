"""Data models and storage matching Store.swift."""

from __future__ import annotations
import hashlib
import json
import os
import re
import threading
import time
import urllib.parse
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

from clipbar.clipboard import Clipboard, ImageStore
from clipbar.settings import Settings, get_data_dir
from clipbar.main_thread import run_on_main
from clipbar.vault import Vault


class Paths:
    support = get_data_dir()
    images = support / "images"
    history = support / "history.json"
    saved = support / "saved.json"
    drafts = support / "drafts.json"


class ClipItem:
    """Represents a clipboard history item, saved item, or draft."""

    def __init__(
        self,
        id: Optional[str] = None,
        text: str = "",
        image: Optional[str] = None,
        files: Optional[List[str]] = None,
        source: Optional[str] = None,
        date: Optional[datetime] = None,
        pinned: bool = False,
        uses: int = 0,
        title: Optional[str] = None,
        secret: Optional[bool] = None,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.text: str = text
        self.image: Optional[str] = image
        self.files: Optional[List[str]] = files
        self.source: Optional[str] = source
        self.date: datetime = date or datetime.now(timezone.utc)
        self.pinned: bool = pinned
        self.uses: int = uses
        self.title: Optional[str] = title
        self.secret: Optional[bool] = secret

    @property
    def is_locked(self) -> bool:
        return self.secret is True

    @property
    def kind(self) -> str:
        if self.image:
            return "image"
        if self.files:
            return "files"
        if self.color:
            return "color"
        if self.url:
            return "link"
        return "text"

    @property
    def preview(self) -> str:
        if self.is_locked:
            return "••••••••"
        if self.kind == "image":
            return f"Image — {self._collapsed(self.text)}" if self.text else "Image"
        if self.kind == "files":
            return ", ".join(Path(f).name for f in (self.files or []))
        return self._collapsed(self.text)

    @property
    def url(self) -> Optional[str]:
        if self.image or self.files or len(self.text.encode("utf-8")) >= 2048:
            return None
        trimmed = self.text.strip()
        if any(c.isspace() for c in trimmed):
            return None
        try:
            parsed = urllib.parse.urlparse(trimmed)
            scheme = parsed.scheme.lower()
            if (scheme in ("http", "https") and parsed.netloc) or scheme == "mailto":
                return trimmed
        except Exception:
            pass
        return None

    @property
    def color(self) -> Optional[str]:
        """Parses #rgb, #rrggbb and #rrggbbaa hex colors."""
        if self.image or self.files or len(self.text.encode("utf-8")) > 12:
            return None
        hex_val = self.text.strip()
        if not hex_val.startswith("#"):
            return None
        hex_digits = hex_val[1:]
        if len(hex_digits) == 3:
            hex_digits = "".join(f"{c}{c}" for c in hex_digits)
        if len(hex_digits) in (6, 8) and all(c in "0123456789abcdefABCDEF" for c in hex_digits):
            return f"#{hex_digits.upper()}"
        return None

    def has_same_content(self, other: ClipItem) -> bool:
        if self.image is not None:
            return self.image == other.image
        if self.files is not None:
            return self.files == other.files
        return other.image is None and other.files is None and self.text == other.text

    @staticmethod
    def _collapsed(text: str) -> str:
        words = text[:160].split()
        return " ".join(words)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "text": self.text,
            "image": self.image,
            "files": self.files,
            "source": self.source,
            "date": self.date.isoformat(),
            "pinned": self.pinned,
            "uses": self.uses,
            "title": self.title,
            "secret": self.secret,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> ClipItem:
        date_val = None
        if "date" in d and d["date"]:
            try:
                date_val = datetime.fromisoformat(d["date"])
            except Exception:
                pass
        return cls(
            id=d.get("id"),
            text=d.get("text", ""),
            image=d.get("image"),
            files=d.get("files"),
            source=d.get("source"),
            date=date_val,
            pinned=d.get("pinned", False),
            uses=d.get("uses", 0),
            title=d.get("title"),
            secret=d.get("secret"),
        )


class Filter(str, Enum):
    ALL = "All"
    PINNED = "Pinned"
    TEXT = "Text"
    LINKS = "Links"
    IMAGES = "Images"
    FILES = "Files"

    def matches(self, item: ClipItem) -> bool:
        if self == Filter.ALL:
            return True
        if self == Filter.PINNED:
            return item.pinned
        if self == Filter.TEXT:
            return item.kind in ("text", "color")
        if self == Filter.LINKS:
            return item.kind == "link"
        if self == Filter.IMAGES:
            return item.kind == "image"
        if self == Filter.FILES:
            return item.kind == "files"
        return True

    @property
    def empty_info(self) -> Tuple[str, str]:
        if self == Filter.ALL:
            return ("Nothing copied yet", "clipboard")
        if self == Filter.PINNED:
            return ("No pinned items", "pin")
        if self == Filter.TEXT:
            return ("No text", "text")
        if self == Filter.LINKS:
            return ("No links", "link")
        if self == Filter.IMAGES:
            return ("No images", "photo")
        if self == Filter.FILES:
            return ("No files", "document")
        return ("Empty", "clipboard")


class ClipStore:
    """History model, capture, cleanup, limits, and persistence matching ClipStore."""

    MAX_TEXT_BYTES = 4_000_000
    MAX_IMAGE_BYTES = 50_000_000

    def __init__(self) -> None:
        self.items: List[ClipItem] = []
        self.saved: List[ClipItem] = []
        self.drafts: List[ClipItem] = []
        self.mode: str = "history"  # "history", "drafts", "saved"
        self.query: str = ""
        self.filter: Filter = Filter.ALL
        self.visible: List[ClipItem] = []
        self.selection: Optional[str] = None
        self.paused: bool = False
        self.toast: Optional[str] = None
        self.focus_request: int = 0

        self._listeners: List[Callable[[], None]] = []
        self._last_content_hash: Optional[str] = None
        self._io_lock = threading.Lock()

    def add_listener(self, cb: Callable[[], None]) -> None:
        if cb not in self._listeners:
            self._listeners.append(cb)

    def remove_listener(self, cb: Callable[[], None]) -> None:
        if cb in self._listeners:
            self._listeners.remove(cb)

    def _notify(self) -> None:
        # Listeners redraw widgets, so they always run on the GUI thread.
        run_on_main(self._notify_now)

    def _notify_now(self) -> None:
        self.refresh()
        for listener in list(self._listeners):
            try:
                listener()
            except Exception:
                pass

    @property
    def selected_item(self) -> Optional[ClipItem]:
        for it in self.visible:
            if it.id == self.selection:
                return it
        return None

    # MARK: - Capture

    def poll_clipboard(
        self,
        text: Optional[str] = None,
        files: Optional[List[str]] = None,
        image_data: Optional[bytes] = None,
        source: Optional[str] = None,
        mime_types: Optional[List[str]] = None,
    ) -> None:
        if self.paused:
            return

        settings = Settings.shared()
        if mime_types and Clipboard.should_ignore(mime_types, skip_concealed=settings.skip_sensitive):
            return

        # Check content duplication with last hash
        content_key = None
        if files:
            content_key = f"files:{sorted(files)}"
        elif text:
            content_key = f"text:{text}"
        elif image_data:
            content_key = f"img:{hashlib.sha256(image_data).hexdigest()}"

        if not content_key or content_key == self._last_content_hash:
            return
        self._last_content_hash = content_key

        if files:
            valid_files = [f for f in files if Path(f).exists()]
            if valid_files:
                self.insert(ClipItem(text="\n".join(valid_files), files=valid_files, source=source))
        elif text:
            trimmed = text.strip()
            if trimmed and len(text.encode("utf-8")) <= self.MAX_TEXT_BYTES:
                if not (settings.skip_sensitive and Clipboard.looks_sensitive(trimmed)):
                    self.insert(ClipItem(text=text, source=source))
        elif image_data and len(image_data) <= self.MAX_IMAGE_BYTES:
            self.capture_image(image_data, is_png=True, source=source)

    def add_screenshot(self, path: Path, copy_to_clipboard: bool = True) -> None:
        if self.paused or not path.exists():
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception:
            return
        is_png = path.suffix.lower() == ".png"
        if copy_to_clipboard:
            try:
                from clipbar.qt import QApplication, QImage
                cb = QApplication.clipboard()
                img = QImage(str(path))
                if not img.isNull():
                    cb.setImage(img)
            except Exception:
                pass
        self.capture_image(data, is_png=is_png, source="Screenshot")

    def capture_image(self, data: bytes, is_png: bool, source: Optional[str] = None) -> None:
        def worker():
            # Writing the file and OCR happen here; the lists change on the GUI thread.
            name = ImageStore.store(data, is_png=is_png)
            if not name:
                return
            run_on_main(lambda: self.insert(ClipItem(image=name, source=source)))
            ocr_text = ImageStore.recognize_text(name)
            if ocr_text:
                run_on_main(lambda: self._set_recognized_text(name, ocr_text))

        threading.Thread(target=worker, daemon=True).start()

    def _set_recognized_text(self, image: str, text: str) -> None:
        for it in self.items:
            if it.image == image:
                it.text = text
        self._notify()
        self.save()

    def insert(self, new_item: ClipItem) -> None:
        existing_idx = None
        for i, item in enumerate(self.items):
            if item.has_same_content(new_item):
                existing_idx = i
                break

        if existing_idx is not None:
            old = self.items.pop(existing_idx)
            new_item.id = old.id
            new_item.pinned = old.pinned
            new_item.uses = old.uses
            if not new_item.text and old.text:
                new_item.text = old.text

        # Insertion index: if pinned -> top; else right after pinned items
        insert_idx = 0 if new_item.pinned else sum(1 for it in self.items if it.pinned)
        self.items.insert(insert_idx, new_item)
        self.apply_limits()
        self._notify()
        self.save()

    # MARK: - Actions

    def copy(self, item: ClipItem) -> None:
        try:
            from clipbar.qt import QApplication, QImage, QUrl
            cb = QApplication.clipboard()
            if item.kind == "image" and item.image:
                img_path = ImageStore.url(item.image)
                if img_path.exists():
                    img = QImage(str(img_path))
                    cb.setImage(img)
            elif item.kind == "files" and item.files:
                cb.setText("\n".join(item.files))
            else:
                cb.setText(item.text)
        except Exception:
            pass

        # Update uses and date
        for it in self.items + self.saved + self.drafts:
            if it.id == item.id:
                it.uses += 1
                it.date = datetime.now(timezone.utc)
        self._notify()
        self.save()

    def toggle_pin(self, item: ClipItem) -> None:
        for i, it in enumerate(self.items):
            if it.id == item.id:
                moved = self.items.pop(i)
                moved.pinned = not moved.pinned
                insert_idx = 0 if moved.pinned else sum(1 for x in self.items if x.pinned)
                self.items.insert(insert_idx, moved)
                break
        self._notify()
        self.save()

    def move_to_top(self, item: ClipItem) -> None:
        for i, it in enumerate(self.items):
            if it.id == item.id:
                moved = self.items.pop(i)
                insert_idx = 0 if moved.pinned else sum(1 for x in self.items if x.pinned)
                self.items.insert(insert_idx, moved)
                self.selection = item.id
                break
        self._notify()
        self.save()

    def move(self, item_id: str, target_id: str, after: bool) -> None:
        target_list = self.items if self.mode == "history" else (self.saved if self.mode == "saved" else self.drafts)
        from_idx = next((i for i, it in enumerate(target_list) if it.id == item_id), None)
        to_idx = next((i for i, it in enumerate(target_list) if it.id == target_id), None)
        if from_idx is not None and to_idx is not None and from_idx != to_idx:
            moved = target_list.pop(from_idx)
            # Re-find to_idx after pop
            new_to_idx = next((i for i, it in enumerate(target_list) if it.id == target_id), 0)
            target_list.insert(new_to_idx + 1 if after else new_to_idx, moved)
            self.selection = item_id
            self._notify()
            self.save()

    def update_text(self, item_id: str, text: str) -> None:
        for it in self.items + self.saved + self.drafts:
            if it.id == item_id:
                it.text = text
                break
        self._notify()
        self.save()

    def remove(self, item: ClipItem) -> None:
        if item.is_locked:
            if not Vault.authenticate(reason=f'delete "{item.title or "a locked item"}"'):
                return
            if not Vault.delete(item.id):
                return

        # Update selection neighbor
        if self.selection == item.id and self.visible:
            idx = next((i for i, it in enumerate(self.visible) if it.id == item.id), 0)
            neighbor = idx + 1 if idx + 1 < len(self.visible) else idx - 1
            self.selection = self.visible[neighbor].id if 0 <= neighbor < len(self.visible) else None

        self.items = [it for it in self.items if it.id != item.id]
        self.saved = [it for it in self.saved if it.id != item.id]
        self.drafts = [it for it in self.drafts if it.id != item.id]
        self._notify()
        self.save()

    # MARK: - Saved Items

    def add_saved(self, title: str, text: str, locked: bool) -> bool:
        item = ClipItem(title=title.strip() or None)
        if locked:
            if not Vault.write(text, item.id):
                return False
            item.text = ""
            item.secret = True
        else:
            item.text = text
            item.secret = None
        self.saved.insert(0, item)
        self.selection = item.id
        self._notify()
        self.save()
        return True

    def update_saved(self, item_id: str, title: str, text: str, locked: bool) -> bool:
        for it in self.saved:
            if it.id == item_id:
                # Nothing changes unless the vault accepted the change.
                if locked:
                    if not Vault.write(text, it.id):
                        return False
                    it.text = ""
                    it.secret = True
                else:
                    if it.is_locked and not Vault.delete(it.id):
                        return False
                    it.text = text
                    it.secret = None
                it.title = title.strip() or None
                break
        self._notify()
        self.save()
        return True

    def rename_saved(self, item_id: str, title: str) -> None:
        for it in self.saved:
            if it.id == item_id:
                it.title = title.strip() or None
                break
        self._notify()
        self.save()

    def unlocked(self, item: ClipItem) -> Optional[ClipItem]:
        if not item.is_locked:
            return item
        if not Vault.authenticate(reason=f'use "{item.title or "a locked item"}"'):
            return None
        secret_val = Vault.read(item.id)
        if secret_val is None:
            return None
        clone = ClipItem.from_dict(item.to_dict())
        clone.text = secret_val
        return clone

    def copy_unlocking(self, item: ClipItem) -> None:
        ready = self.unlocked(item)
        if ready:
            self.copy(ready)
            self.flash("Copied")

    def save_item(self, item: ClipItem) -> None:
        """Moves a history item or draft into Saved."""
        moved = None
        for i, it in enumerate(self.items):
            if it.id == item.id:
                moved = self.items.pop(i)
                break
        if not moved:
            for i, it in enumerate(self.drafts):
                if it.id == item.id:
                    moved = self.drafts.pop(i)
                    break
        if moved:
            moved.pinned = False
            self.saved.insert(0, moved)
            self.flash("Moved to Saved")
            self._notify()
            self.save()

    def unsave(self, item: ClipItem) -> None:
        for i, it in enumerate(self.saved):
            if it.id == item.id:
                moved = self.saved.pop(i)
                moved.date = datetime.now(timezone.utc)
                insert_idx = sum(1 for x in self.items if x.pinned)
                self.items.insert(insert_idx, moved)
                self.flash("Moved to History")
                self._notify()
                self.save()
                break

    # MARK: - Drafts

    def record_draft(self, draft_id: Optional[str], text: str, source: Optional[str]) -> str:
        # A field revisited, or text continuing an earlier draft
        existing_idx = None
        if draft_id:
            existing_idx = next((i for i, it in enumerate(self.drafts) if it.id == draft_id), None)
        if existing_idx is None and source:
            existing_idx = next(
                (i for i, it in enumerate(self.drafts) if it.source == source and self._continues(text, it.text)),
                None
            )

        if existing_idx is not None:
            draft = self.drafts.pop(existing_idx)
        else:
            draft = ClipItem()

        # Remove redundant older drafts from the same source
        self.drafts = [
            it for it in self.drafts
            if not (it.source == source and self._continues(text, it.text))
        ]

        draft.text = text
        draft.source = source
        draft.date = datetime.now(timezone.utc)
        self.drafts.insert(0, draft)
        self.apply_limits()
        self._notify()
        # Save drafts atomically
        self._save_drafts_only()
        return draft.id

    @staticmethod
    def _continues(current: str, earlier: str) -> bool:
        shorter = min(len(current), len(earlier))
        if shorter == 0:
            return False
        common_len = 0
        for c1, c2 in zip(current, earlier):
            if c1 == c2:
                common_len += 1
            else:
                break
        return common_len * 10 >= shorter * 7

    def clear_drafts(self) -> None:
        self.drafts.clear()
        self._notify()
        self.save()

    def clear(self, including_pinned: bool = False) -> None:
        if including_pinned:
            self.items.clear()
        else:
            self.items = [it for it in self.items if it.pinned]
        self._notify()
        self.save()

    def is_draft(self, item: ClipItem) -> bool:
        return any(it.id == item.id for it in self.drafts)

    def is_saved(self, item: ClipItem) -> bool:
        return any(it.id == item.id for it in self.saved)

    def item_with_id(self, item_id: str) -> Optional[ClipItem]:
        for it in self.items + self.saved + self.drafts:
            if it.id == item_id:
                return it
        return None

    def flash(self, message: str) -> None:
        self.toast = message
        self._notify()

        def clear_toast():
            time.sleep(1.6)
            run_on_main(lambda: self._clear_toast(message))

        threading.Thread(target=clear_toast, daemon=True).start()

    def _clear_toast(self, message: str) -> None:
        if self.toast == message:
            self.toast = None
            self._notify()

    # MARK: - Navigation & Refresh

    def prepare_for_display(self) -> None:
        self.query = ""
        self.filter = Filter.ALL
        self.apply_limits()
        self.refresh()
        self.selection = self.visible[0].id if self.visible else None
        self.focus_request += 1
        self._notify()

    def move_selection(self, delta: int) -> None:
        if not self.visible:
            return
        idx = next((i for i, it in enumerate(self.visible) if it.id == self.selection), 0)
        new_idx = max(0, min(len(self.visible) - 1, idx + delta))
        self.selection = self.visible[new_idx].id
        self._notify()

    def cycle_filter(self, delta: int) -> None:
        all_cases = list(Filter)
        curr = all_cases.index(self.filter) if self.filter in all_cases else 0
        self.filter = all_cases[(curr + delta) % len(all_cases)]
        self._notify()

    def refresh(self) -> None:
        terms = self.query.lower().split()
        if self.mode == "history":
            source = [it for it in self.items if self.filter.matches(it)]
        elif self.mode == "drafts":
            source = list(self.drafts)
        else:
            source = list(self.saved)

        if not terms:
            self.visible = source
        else:
            filtered = []
            for it in source:
                text_match = all(t in it.text.lower() for t in terms)
                title_match = (it.title and all(t in it.title.lower() for t in terms))
                if text_match or title_match:
                    filtered.append(it)
            self.visible = filtered

        if self.selection not in [it.id for it in self.visible]:
            self.selection = self.visible[0].id if self.visible else None

    # MARK: - Limits and Pruning

    def apply_limits(self) -> None:
        settings = Settings.shared()
        # Prune drafts
        cutoff_drafts = time.time() - (settings.draft_hours * 3600)
        valid_drafts = []
        for it in self.drafts:
            if it.date.timestamp() >= cutoff_drafts:
                valid_drafts.append(it)
                if len(valid_drafts) >= settings.draft_count:
                    break
        self.drafts = valid_drafts

        # Prune history
        cutoff_history = time.time() - (settings.keep_days * 86400)
        keep_pinned = not settings.clean_pinned
        max_items = settings.max_items
        kept_count = 0
        pruned_history = []
        for it in self.items:
            if it.pinned and keep_pinned:
                pruned_history.append(it)
                continue
            if it.date.timestamp() >= cutoff_history and kept_count < max_items:
                pruned_history.append(it)
                kept_count += 1
        self.items = pruned_history

    # MARK: - Persistence

    def load(self) -> None:
        with self._io_lock:
            # Saved
            if Paths.saved.exists():
                try:
                    with open(Paths.saved, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.saved = [ClipItem.from_dict(d) for d in data]
                except Exception:
                    pass

            # Drafts
            if Paths.drafts.exists():
                try:
                    with open(Paths.drafts, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.drafts = [ClipItem.from_dict(d) for d in data]
                except Exception:
                    pass

            # History
            if Paths.history.exists():
                try:
                    with open(Paths.history, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    items = [ClipItem.from_dict(d) for d in data]
                    # Filter out empty items
                    self.items = [
                        it for it in items
                        if it.image or it.files or it.text
                    ]
                except Exception:
                    pass

            self.apply_limits()
            self.refresh()

            # Clean orphaned images
            referenced = {it.image for it in (self.items + self.saved) if it.image}
            ImageStore.purge(referenced)

    def _save_drafts_only(self) -> None:
        # Copy the lists now; the thread only writes files.
        drafts = [it.to_dict() for it in self.drafts]

        def worker():
            with self._io_lock:
                temp = Paths.drafts.with_suffix(".tmp")
                try:
                    with open(temp, "w", encoding="utf-8") as f:
                        json.dump(drafts, f, indent=2)
                    temp.replace(Paths.drafts)
                except Exception:
                    if temp.exists():
                        try:
                            temp.unlink()
                        except Exception:
                            pass

        threading.Thread(target=worker, daemon=True).start()

    def save(self) -> None:
        # Copy the lists now; the thread only writes files.
        items = [it.to_dict() for it in self.items]
        saved = [it.to_dict() for it in self.saved]
        drafts = [it.to_dict() for it in self.drafts]

        def worker():
            with self._io_lock:
                # History
                temp_h = Paths.history.with_suffix(".tmp")
                try:
                    with open(temp_h, "w", encoding="utf-8") as f:
                        json.dump(items, f, indent=2)
                    temp_h.replace(Paths.history)
                except Exception:
                    if temp_h.exists():
                        try:
                            temp_h.unlink()
                        except Exception:
                            pass

                # Saved
                temp_s = Paths.saved.with_suffix(".tmp")
                try:
                    with open(temp_s, "w", encoding="utf-8") as f:
                        json.dump(saved, f, indent=2)
                    temp_s.replace(Paths.saved)
                except Exception:
                    if temp_s.exists():
                        try:
                            temp_s.unlink()
                        except Exception:
                            pass

                # Drafts
                temp_d = Paths.drafts.with_suffix(".tmp")
                try:
                    with open(temp_d, "w", encoding="utf-8") as f:
                        json.dump(drafts, f, indent=2)
                    temp_d.replace(Paths.drafts)
                except Exception:
                    if temp_d.exists():
                        try:
                            temp_d.unlink()
                        except Exception:
                            pass

        threading.Thread(target=worker, daemon=True).start()
