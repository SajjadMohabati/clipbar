"""Settings window matching SettingsView.swift."""

from __future__ import annotations
import os
import subprocess
from pathlib import Path
from typing import Optional

from clipbar.clipboard import Clipboard
from clipbar.qt import (
    QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QStackedLayout, QCheckBox, QSpinBox,
    QComboBox, QPushButton, QDialog, QLineEdit, Qt, QIcon, QSize
)
from clipbar.settings import Settings, get_config_dir, get_data_dir
from clipbar.store import ClipStore
from clipbar.styles import LIQUID_GLASS_QSS, get_icon, switch_qss, tile_icon


def is_autostart_enabled() -> bool:
    desktop_file = Path.home() / ".config" / "autostart" / "clipbar.desktop"
    return desktop_file.exists()


def set_autostart(enabled: bool) -> None:
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    desktop_file = autostart_dir / "clipbar.desktop"
    if enabled:
        content = """[Desktop Entry]
Type=Application
Name=ClipBar
Comment=Clipboard Manager for Linux
Exec=clipbar
Icon=clipbar
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
"""
        try:
            with open(desktop_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass
    else:
        if desktop_file.exists():
            try:
                desktop_file.unlink()
            except Exception:
                pass


class SettingsView(QMainWindow):
    """Full preferences window with sidebar navigation matching SettingsView.swift."""

    # Same symbols and colors as the Mac settings sidebar.
    PANES = {
        "General": ("gear", "#8e8e93"),
        "Pasting": ("paste", "#0a84ff"),
        "Screenshots": ("camera", "#bf5af2"),
        "Drafts": ("drafts", "#30d158"),
        "Privacy": ("hand", "#5e5ce6"),
        "History": ("clock_arrow", "#ff9f0a"),
        "About": ("info", "#40c8e0"),
    }

    def __init__(self, store: ClipStore, parent=None):
        super().__init__(parent)
        self.store = store
        self.settings = Settings.shared()

        self.setWindowTitle("ClipBar Settings")
        self.resize(720, 520)
        self.setStyleSheet(LIQUID_GLASS_QSS + switch_qss() + "QLabel { color: rgba(255, 255, 255, 0.85); }"
            "QSpinBox, QComboBox { background: rgba(255, 255, 255, 0.08); color: #ffffff;"
            " border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 7px; padding: 4px 8px; min-width: 70px; }"
            "QComboBox QAbstractItemView { background: #1e232c; color: #ffffff; selection-background-color: #0a84ff; }")

        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("SettingsSidebar")
        sidebar.setStyleSheet(
            "QFrame#SettingsSidebar { background: rgba(22, 28, 36, 0.98); border-right: 1px solid rgba(255, 255, 255, 0.1); }"
        )
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(10, 14, 10, 14)
        sb_layout.setSpacing(4)

        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet(
            "QListWidget { background: transparent; border: none; outline: none; }"
            "QListWidget::item { padding: 8px 12px; border-radius: 8px; color: rgba(255, 255, 255, 0.7); font-size: 13px; font-weight: 500; }"
            "QListWidget::item:hover { background: rgba(255, 255, 255, 0.08); color: #ffffff; }"
            "QListWidget::item:selected { background: rgba(255, 255, 255, 0.16); color: #ffffff; font-weight: 600; }"
        )

        self.nav_list.setIconSize(QSize(22, 22))
        for title, (icon_name, tint) in self.PANES.items():
            self.nav_list.addItem(QListWidgetItem(tile_icon(icon_name, tint), title))

        sb_layout.addWidget(self.nav_list)
        main_layout.addWidget(sidebar)

        # 2. Right Content Stack
        self.content_stack = QStackedLayout()
        content_container = QWidget()
        content_container.setObjectName("SettingsContent")
        content_container.setStyleSheet("QWidget#SettingsContent { background: rgba(18, 22, 30, 0.95); }")
        self.content_stack.setContentsMargins(28, 22, 28, 22)
        content_container.setLayout(self.content_stack)

        self.content_stack.addWidget(self._create_general_pane())
        self.content_stack.addWidget(self._create_pasting_pane())
        self.content_stack.addWidget(self._create_screenshots_pane())
        self.content_stack.addWidget(self._create_drafts_pane())
        self.content_stack.addWidget(self._create_privacy_pane())
        self.content_stack.addWidget(self._create_history_pane())
        self.content_stack.addWidget(self._create_about_pane())

        self.nav_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        self.nav_list.setCurrentRow(0)

        main_layout.addWidget(content_container, 1)

    # MARK: - Panes

    def _create_general_pane(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        layout.addWidget(self._pane_header("General", "Startup and the shortcut that opens ClipBar."))

        # Autostart
        chk_autostart = QCheckBox("Launch at login")
        chk_autostart.setChecked(is_autostart_enabled())
        chk_autostart.toggled.connect(set_autostart)
        layout.addWidget(chk_autostart)

        # Pause
        chk_pause = QCheckBox("Pause capturing")
        chk_pause.setChecked(self.store.paused)
        chk_pause.toggled.connect(lambda c: setattr(self.store, "paused", c))
        layout.addWidget(chk_pause)

        # Shortcut
        s_box = QFrame()
        s_box.setObjectName("s_boxCard")
        s_box.setStyleSheet("QFrame#s_boxCard { background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 12px; }")
        sb_layout = QHBoxLayout(s_box)
        sb_layout.addWidget(QLabel("Global Shortcut:"))
        shortcut_input = QLineEdit(self.settings.shortcut)
        shortcut_input.setStyleSheet("background: rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 4px 8px; color: #ffffff;")
        shortcut_input.textChanged.connect(lambda t: setattr(self.settings, "shortcut", t))
        sb_layout.addWidget(shortcut_input)
        layout.addWidget(s_box)

        layout.addStretch()
        return w

    def _create_pasting_pane(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        layout.addWidget(self._pane_header("Pasting", "Send the chosen item straight into the app you were using."))

        chk_autopaste = QCheckBox("Paste into the active app")
        chk_autopaste.setChecked(self.settings.auto_paste)
        chk_autopaste.toggled.connect(lambda c: setattr(self.settings, "auto_paste", c))
        layout.addWidget(chk_autopaste)

        # Status box
        status_box = QFrame()
        status_box.setObjectName("status_boxCard")
        status_box.setStyleSheet("QFrame#status_boxCard { background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 12px; }")
        st_layout = QVBoxLayout(status_box)
        can_paste = Clipboard.can_paste()
        st_title = QLabel("Permission / Paste Utility:" + (" ✓ Detected" if can_paste else " ⚠ Tool missing"))
        st_title.setStyleSheet(f"font-weight: 600; color: {'#51cf66' if can_paste else '#f59f00'};")
        st_desc = QLabel(
            "ClipBar simulates Ctrl+V to paste automatically into other apps.\n"
            + ("Ready on this system." if can_paste else "Install xdotool (for X11) or wtype/ydotool (for Wayland) to enable direct pasting.")
        )
        st_desc.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 12px;")
        st_layout.addWidget(st_title)
        st_layout.addWidget(st_desc)
        layout.addWidget(status_box)

        layout.addStretch()
        return w

    def _create_screenshots_pane(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        layout.addWidget(self._pane_header("Screenshots", "Every screenshot you take lands in your history, ready to paste."))

        chk_capture = QCheckBox("Add new screenshots to history")
        chk_capture.setChecked(self.settings.capture_screenshots)
        chk_capture.toggled.connect(lambda c: setattr(self.settings, "capture_screenshots", c))
        layout.addWidget(chk_capture)

        chk_copy = QCheckBox("Copy them to the clipboard")
        chk_copy.setChecked(self.settings.copy_screenshots)
        chk_copy.toggled.connect(lambda c: setattr(self.settings, "copy_screenshots", c))
        layout.addWidget(chk_copy)

        hint = QLabel("💡 Tip: ClipBar watches your default screenshot directory (~/Pictures/Screenshots) and runs on-device OCR so text in screenshots is searchable.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 12px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px;")
        layout.addWidget(hint)

        layout.addStretch()
        return w

    def _create_drafts_pane(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        layout.addWidget(self._pane_header("Drafts", "Never lose a message you typed: ClipBar keeps a copy while you write."))

        chk_drafts = QCheckBox("Keep what I type in other apps")
        chk_drafts.setChecked(self.settings.drafts_enabled)
        chk_drafts.toggled.connect(lambda c: setattr(self.settings, "drafts_enabled", c))
        layout.addWidget(chk_drafts)

        from clipbar.draft_watcher import DraftWatcher
        if not DraftWatcher.is_available():
            missing = QLabel("Drafts needs Linux Accessibility: sudo apt install python3-gi gir1.2-atspi-2.0 at-spi2-core")
            missing.setWordWrap(True)
            missing.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            missing.setStyleSheet("color: #ff9f0a; font-size: 11px;")
            layout.addWidget(missing)

        # Min length
        len_row = QHBoxLayout()
        len_row.addWidget(QLabel("Only text longer than:"))
        spin_len = QSpinBox()
        spin_len.setRange(10, 500)
        spin_len.setValue(self.settings.draft_min_length)
        spin_len.valueChanged.connect(lambda v: setattr(self.settings, "draft_min_length", v))
        len_row.addWidget(spin_len)
        len_row.addWidget(QLabel("characters"))
        len_row.addStretch()
        layout.addLayout(len_row)

        # How long and how many, with the same choices and limits as the Mac app
        hours_row = QHBoxLayout()
        hours_row.addWidget(QLabel("Keep drafts for:"))
        combo_hours = QComboBox()
        choices = [1, 3, 6, 12, 24, 72, 168]
        for hours in choices:
            label = (f"{hours} hour" + ("s" if hours > 1 else "")) if hours < 24 else (
                "1 day" if hours == 24 else f"{hours // 24} days")
            combo_hours.addItem(label, hours)
        combo_hours.setCurrentIndex(choices.index(self.settings.draft_hours) if self.settings.draft_hours in choices else 3)
        combo_hours.currentIndexChanged.connect(
            lambda i: setattr(self.settings, "draft_hours", combo_hours.itemData(i)))
        hours_row.addWidget(combo_hours)
        hours_row.addStretch()
        layout.addLayout(hours_row)

        count_row = QHBoxLayout()
        count_row.addWidget(QLabel("Keep at most:"))
        spin_count = QSpinBox()
        spin_count.setRange(1, 50)
        spin_count.setValue(self.settings.draft_count)
        spin_count.valueChanged.connect(lambda v: setattr(self.settings, "draft_count", v))
        count_row.addWidget(spin_count)
        count_row.addWidget(QLabel("drafts"))
        count_row.addStretch()
        layout.addLayout(count_row)

        # Clear drafts button
        btn_clear_d = QPushButton("Clear Drafts")
        btn_clear_d.setStyleSheet("background: rgba(224, 49, 49, 0.2); color: #ff6b6b; border-radius: 6px; padding: 6px 12px; max-width: 140px;")
        btn_clear_d.clicked.connect(self.store.clear_drafts)
        layout.addWidget(btn_clear_d)

        desc = QLabel(
            "ClipBar polls the focused text field once a second via AT-SPI2 accessibility.\n"
            "It never records raw keystrokes, never reads password or search fields, and skips terminals,\n"
            "password managers and any app it can't identify, on X11 and Wayland alike.\n"
            "Drafts stay entirely on this machine."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: rgba(255, 255, 255, 0.55); font-size: 11px;")
        layout.addWidget(desc)

        layout.addStretch()
        return w

    def _create_privacy_pane(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        layout.addWidget(self._pane_header("Privacy", "Keep passwords and secrets out of your history."))

        chk_sensitive = QCheckBox("Ignore passwords and secrets")
        chk_sensitive.setChecked(self.settings.skip_sensitive)
        chk_sensitive.toggled.connect(lambda c: setattr(self.settings, "skip_sensitive", c))
        layout.addWidget(chk_sensitive)

        note = QLabel("🔒 Everything stays on this PC. No network requests, no telemetry, no cloud sync.")
        note.setStyleSheet("color: rgba(255, 255, 255, 0.65); font-size: 12px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px;")
        layout.addWidget(note)

        layout.addStretch()
        return w

    def _create_history_pane(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)

        layout.addWidget(self._pane_header("History", "How long items are kept, and how many."))

        # Keep days
        d_row = QHBoxLayout()
        d_row.addWidget(QLabel("Keep items for:"))
        spin_days = QSpinBox()
        spin_days.setRange(1, 365)
        spin_days.setValue(self.settings.keep_days)
        spin_days.valueChanged.connect(lambda v: setattr(self.settings, "keep_days", v))
        d_row.addWidget(spin_days)
        d_row.addWidget(QLabel("days"))
        d_row.addStretch()
        layout.addLayout(d_row)

        # Max count
        c_row = QHBoxLayout()
        c_row.addWidget(QLabel("Keep at most:"))
        spin_max = QSpinBox()
        spin_max.setRange(50, 2000)
        spin_max.setSingleStep(50)
        spin_max.setValue(self.settings.max_items)
        spin_max.valueChanged.connect(lambda v: setattr(self.settings, "max_items", v))
        c_row.addWidget(spin_max)
        c_row.addWidget(QLabel("items"))
        c_row.addStretch()
        layout.addLayout(c_row)

        chk_clean_pinned = QCheckBox("Clean up pinned items too")
        chk_clean_pinned.setChecked(self.settings.clean_pinned)
        chk_clean_pinned.toggled.connect(lambda c: setattr(self.settings, "clean_pinned", c))
        layout.addWidget(chk_clean_pinned)

        btn_clear_h = QPushButton("Clear History…")
        btn_clear_h.setStyleSheet("background: rgba(224, 49, 49, 0.2); color: #ff6b6b; border-radius: 6px; padding: 6px 12px; max-width: 140px;")
        btn_clear_h.clicked.connect(lambda: self.store.clear(including_pinned=False))
        layout.addWidget(btn_clear_h)

        layout.addStretch()
        return w

    def _create_about_pane(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        icon_lbl = QLabel()
        app_icon = Path(__file__).resolve().parent.parent / "resources" / "clipbar.png"
        icon_lbl.setPixmap(QIcon(str(app_icon)).pixmap(112, 112))
        layout.addWidget(icon_lbl)

        title = QLabel("ClipBar")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #ffffff;")
        layout.addWidget(title)

        ver = QLabel("Version 1.0 (Linux)")
        ver.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 13px;")
        layout.addWidget(ver)

        desc = QLabel("A fast, private clipboard history for Linux.\nBuilt with Liquid Glass design.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 13px;")
        layout.addWidget(desc)

        author = QLabel("Created by Sajjad Mohabati · MIT License")
        author.setStyleSheet("color: rgba(255, 255, 255, 0.4); font-size: 11px;")
        layout.addWidget(author)

        btn_gh = QPushButton("View on GitHub")
        btn_gh.setStyleSheet("background: rgba(255, 255, 255, 0.12); color: #ffffff; border-radius: 8px; padding: 6px 16px; font-weight: 600;")
        btn_gh.clicked.connect(lambda: subprocess.Popen(["xdg-open", "https://github.com/SajjadMohabati/clipbar-mac"]))
        layout.addWidget(btn_gh)

        return w

    def _pane_header(self, title: str, subtitle: str) -> QWidget:
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 10)
        row.setSpacing(12)

        icon_name, tint = self.PANES.get(title, ("gear", "#8e8e93"))
        tile = QLabel()
        tile.setPixmap(tile_icon(icon_name, tint, 40).pixmap(40, 40))
        row.addWidget(tile)

        text = QVBoxLayout()
        text.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet("font-size: 17px; font-weight: 700; color: #ffffff;")
        s = QLabel(subtitle)
        s.setWordWrap(True)
        s.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.55);")
        text.addWidget(t)
        text.addWidget(s)
        row.addLayout(text, 1)
        return box
