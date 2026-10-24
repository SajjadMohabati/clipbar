"""ClipView: Main floating panel matching ClipView.swift."""

from __future__ import annotations
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from clipbar.clipboard import Clipboard, Icons, ImageStore
from clipbar.qt import (
    QApplication, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QMenu, QCursor, QDialog,
    QColor, QPixmap, QPainter, QPainterPath, QPen, QBrush, QIcon,
    Qt, QEvent, QTimer, QSize, QSizePolicy
)
from clipbar.settings import Settings
from clipbar.store import ClipItem, ClipStore, Filter
from clipbar.styles import CLIPBAR_QSS, get_icon


def format_relative_time(dt: datetime) -> str:
    """Formats relative time like 'now', '2 min. ago', '1 hr. ago', '3 days ago'."""
    if dt.tzinfo is not None:
        now = datetime.now(timezone.utc)
    else:
        now = datetime.now()
    diff = (now - dt).total_seconds()
    if diff < 0:
        diff = 0
    if diff < 60:
        return "now"
    minutes = int(diff // 60)
    if minutes < 60:
        return f"{minutes} min. ago"
    hours = int(minutes // 60)
    if hours < 24:
        return f"{hours} hr. ago"
    days = int(hours // 24)
    if days == 1:
        return "yesterday"
    return f"{days} days ago"


class ElidedLabel(QLabel):
    """One line of text that ends in "…" instead of widening the row, like the Mac rows."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(" ".join(text.split()), parent)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(10)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.setFont(self.font())
        rect = self.contentsRect()
        elided = self.fontMetrics().elidedText(self.text(), Qt.TextElideMode.ElideRight, rect.width())
        painter.drawText(rect, int(self.alignment()) | int(Qt.AlignmentFlag.AlignVCenter), elided)
        painter.end()


class ItemIconWidget(QWidget):
    """Renders 30x30 rounded icon box with kind-specific tints and pin badge."""

    def __init__(self, item: ClipItem, size: int = 30, parent=None):
        super().__init__(parent)
        self.item = item
        self.box_size = size
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        s = float(self.box_size)
        rect_path = QPainterPath()
        rect_path.addRoundedRect(0, 0, s, s, s * 0.27, s * 0.27)

        # 1. Background / Swatch
        if self.item.is_locked:
            painter.fillPath(rect_path, QColor(247, 103, 7, 45))  # Soft orange
            icon = get_icon("lock", "#f76707")
            if icon:
                icon.paint(painter, int(s * 0.22), int(s * 0.22), int(s * 0.56), int(s * 0.56))
        elif self.item.kind == "color" and self.item.color:
            painter.fillPath(rect_path, QColor(self.item.color))
        elif self.item.kind == "image" and self.item.image:
            thumb = ImageStore.thumbnail(self.item.image, size=int(s * 2))
            if thumb and not thumb.isNull():
                painter.save()
                painter.setClipPath(rect_path)
                painter.drawPixmap(0, 0, int(s), int(s), thumb)
                painter.restore()
            else:
                painter.fillPath(rect_path, QColor(174, 62, 201, 45))  # Soft purple
                icon = get_icon("photo", "#be4bdb")
                if icon:
                    icon.paint(painter, int(s * 0.22), int(s * 0.22), int(s * 0.56), int(s * 0.56))
        elif self.item.kind == "files":
            painter.fillPath(rect_path, QColor(245, 159, 0, 45))  # Soft amber
            first_path = self.item.files[0] if self.item.files else "/"
            icon = Icons.file_icon(first_path)
            if icon and not icon.isNull():
                icon.paint(painter, int(s * 0.18), int(s * 0.18), int(s * 0.64), int(s * 0.64))
            else:
                doc_icon = get_icon("document", "#f59f00")
                if doc_icon:
                    doc_icon.paint(painter, int(s * 0.22), int(s * 0.22), int(s * 0.56), int(s * 0.56))
        elif self.item.kind == "link":
            painter.fillPath(rect_path, QColor(51, 154, 240, 45))  # Soft blue
            icon = get_icon("link", "#339af0")
            if icon:
                icon.paint(painter, int(s * 0.22), int(s * 0.22), int(s * 0.56), int(s * 0.56))
        else:
            # Text
            painter.fillPath(rect_path, QColor(255, 255, 255, 25))  # Soft gray
            icon = get_icon("text", "#ced4da")
            if icon:
                icon.paint(painter, int(s * 0.22), int(s * 0.22), int(s * 0.56), int(s * 0.56))

        # Thin outer stroke
        painter.setPen(QPen(QColor(255, 255, 255, 25), 0.8))
        painter.drawPath(rect_path)

        # 2. Pinned Badge overlay in top right
        if self.item.pinned:
            badge_x = s - 10
            badge_y = 0
            pin_icon = get_icon("pin_fill", "#ffffff")
            if pin_icon:
                painter.save()
                pin_bg = QPainterPath()
                pin_bg.addEllipse(badge_x - 2, badge_y - 2, 14, 14)
                painter.fillPath(pin_bg, QColor(30, 36, 46, 230))
                painter.setPen(QPen(QColor(255, 255, 255, 100), 0.6))
                painter.drawPath(pin_bg)
                pin_icon.paint(painter, int(badge_x), int(badge_y), 10, 10)
                painter.restore()


class ClipRowWidget(QFrame):
    """Row widget representing one item in the list."""

    def __init__(
        self,
        item: ClipItem,
        shortcut_idx: Optional[int],
        selected: bool,
        store: ClipStore,
        on_paste: Callable[[ClipItem, bool], None],
        on_edit: Callable[[ClipItem], None],
        on_rename: Callable[[ClipItem], None],
        parent=None
    ):
        super().__init__(parent)
        self.item = item
        self.shortcut_idx = shortcut_idx
        self.selected = selected
        self.store = store
        self.on_paste = on_paste
        self.on_edit = on_edit
        self.on_rename = on_rename

        self.setObjectName("ClipRow")
        self.setProperty("class", "ClipRowFrame")
        self.setProperty("selected", "true" if selected else "false")
        self.setFixedHeight(46)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 5, 8, 5)
        self.layout.setSpacing(10)

        # Left Icon
        self.icon_widget = ItemIconWidget(item, size=30)
        self.layout.addWidget(self.icon_widget)

        # Middle Titles
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        if item.title:
            self.lbl_title = ElidedLabel(item.title)
            self.lbl_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff;")
            self.lbl_preview = ElidedLabel(item.preview)
            self.lbl_preview.setStyleSheet(
                "font-size: 11px; color: #96999c;"
                + ("font-family: monospace;" if item.is_locked else "")
            )
            text_layout.addWidget(self.lbl_title)
            text_layout.addWidget(self.lbl_preview)
        else:
            self.lbl_preview = ElidedLabel(item.preview)
            self.lbl_preview.setStyleSheet("font-size: 13px; color: #ffffff;")

            meta_parts = []
            if item.source:
                meta_parts.append(item.source.capitalize())
            meta_parts.append(format_relative_time(item.date))
            if item.uses > 0:
                meta_parts.append(f"{item.uses}×")

            self.lbl_meta = ElidedLabel(" · ".join(meta_parts))
            self.lbl_meta.setStyleSheet("font-size: 11px; color: #96999c;")
            text_layout.addWidget(self.lbl_preview)
            text_layout.addWidget(self.lbl_meta)

        self.layout.addLayout(text_layout, 1)

        # Right side: Shortcut badge or hover action buttons
        self.right_container = QWidget()
        self.right_layout = QHBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(2)

        self.shortcut_label = None
        if shortcut_idx is not None:
            self.shortcut_label = QLabel(f"Ctrl {shortcut_idx}")
            self.shortcut_label.setProperty("class", "ShortcutBadge")
            self.right_layout.addWidget(self.shortcut_label)

        # Action buttons (hidden until hover)
        self.btn_pin = QPushButton()
        self.btn_pin.setProperty("class", "RowActionButton")
        self.btn_pin.setIcon(get_icon("pin" if not item.pinned else "pin_fill", "#ced4da"))
        self.btn_pin.setToolTip("Unpin" if item.pinned else "Pin (Ctrl+P)")
        self.btn_pin.clicked.connect(lambda: self.store.toggle_pin(self.item))
        self.right_layout.addWidget(self.btn_pin)

        if not self.store.is_saved(item):
            self.btn_save = QPushButton()
            self.btn_save.setProperty("class", "RowActionButton")
            self.btn_save.setIcon(get_icon("bookmark", "#ced4da"))
            self.btn_save.setToolTip("Move to Saved (Ctrl+S)")
            self.btn_save.clicked.connect(lambda: self.store.save_item(self.item))
            self.right_layout.addWidget(self.btn_save)
        else:
            self.btn_rename = QPushButton()
            self.btn_rename.setProperty("class", "RowActionButton")
            self.btn_rename.setIcon(get_icon("rename", "#ced4da"))
            self.btn_rename.setToolTip("Rename")
            self.btn_rename.clicked.connect(lambda: self.on_rename(self.item))
            self.right_layout.addWidget(self.btn_rename)

        self.btn_edit = QPushButton()
        self.btn_edit.setProperty("class", "RowActionButton")
        self.btn_edit.setIcon(get_icon("edit", "#ced4da"))
        self.btn_edit.setToolTip("View and edit (Ctrl+E)")
        self.btn_edit.clicked.connect(lambda: self.on_edit(self.item))
        self.right_layout.addWidget(self.btn_edit)

        self.btn_delete = QPushButton()
        self.btn_delete.setProperty("class", "RowActionButton")
        self.btn_delete.setProperty("destructive", "true")
        self.btn_delete.setIcon(get_icon("trash", "#fa5252"))
        self.btn_delete.setToolTip("Delete (Ctrl+Backspace)")
        self.btn_delete.clicked.connect(lambda: self.store.remove(self.item))
        self.right_layout.addWidget(self.btn_delete)

        self.set_hover_buttons_visible(False)
        self.layout.addWidget(self.right_container)

    def set_hover_buttons_visible(self, visible: bool) -> None:
        self.btn_pin.setVisible(visible and self.store.mode == "history")
        if hasattr(self, "btn_save"):
            self.btn_save.setVisible(visible)
        if hasattr(self, "btn_rename"):
            self.btn_rename.setVisible(visible)
        self.btn_edit.setVisible(visible)
        self.btn_delete.setVisible(visible)
        if self.shortcut_label:
            self.shortcut_label.setVisible(not visible)

    def enterEvent(self, event):
        self.set_hover_buttons_visible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.set_hover_buttons_visible(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_paste(self.item, True)
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        act_paste = menu.addAction("Paste" if Settings.shared().auto_paste else "Copy and Close")
        act_copy = menu.addAction("Copy")

        if self.item.kind == "image" and self.item.text:
            act_copy_ocr = menu.addAction("Copy Text from Image")
        else:
            act_copy_ocr = None

        if self.item.url:
            act_open_url = menu.addAction("Open Link")
        else:
            act_open_url = None

        if self.item.files:
            act_show_files = menu.addAction("Show in File Manager")
        else:
            act_show_files = None

        menu.addSeparator()

        if self.store.mode == "saved":
            act_rename = menu.addAction("Rename…" if self.item.title else "Add Title…")
            act_edit = menu.addAction("Edit…")
            if not self.item.is_locked:
                act_move_history = menu.addAction("Move to History")
            else:
                act_move_history = None
            act_move_saved = None
            act_pin = None
        else:
            act_rename = None
            act_move_history = None
            act_move_saved = menu.addAction("Move to Saved")
            act_pin = menu.addAction("Unpin" if self.item.pinned else "Pin")
            act_edit = menu.addAction("View and Edit…")

        menu.addSeparator()
        act_delete = menu.addAction("Delete")

        selected = menu.exec(pos)
        if not selected:
            return

        if selected == act_paste:
            self.on_paste(self.item, True)
        elif selected == act_copy:
            self.store.copy_unlocking(self.item)
        elif act_copy_ocr and selected == act_copy_ocr:
            Clipboard.write(self.item.text)
        elif act_open_url and selected == act_open_url and self.item.url:
            import webbrowser
            webbrowser.open(self.item.url)
        elif act_show_files and selected == act_show_files and self.item.files:
            try:
                subprocess.Popen(["xdg-open", str(Path(self.item.files[0]).parent)])
            except Exception:
                pass
        elif act_rename and selected == act_rename:
            self.on_rename(self.item)
        elif act_move_saved and selected == act_move_saved:
            self.store.save_item(self.item)
        elif act_move_history and selected == act_move_history:
            self.store.unsave(self.item)
        elif act_pin and selected == act_pin:
            self.store.toggle_pin(self.item)
        elif selected == act_edit:
            self.on_edit(self.item)
        elif selected == act_delete:
            self.store.remove(self.item)


class SavedItemDialog(QDialog):
    """Popover dialog for adding a new saved item."""

    def __init__(self, on_add: Callable[[str, str, bool], None], parent=None):
        super().__init__(parent)
        self.on_add = on_add
        self.setWindowTitle("New Saved Item")
        self.setFixedSize(300, 240)
        self.setStyleSheet(CLIPBAR_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl = QLabel("New Saved Item")
        lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff;")
        layout.addWidget(lbl)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title, e.g. Bank name")
        self.title_input.setStyleSheet(
            "background: #2d333a; border: 1px solid #454950;"
            "border-radius: 8px; padding: 6px; color: #ffffff;"
        )
        layout.addWidget(self.title_input)

        self.val_input = QLineEdit()
        self.val_input.setPlaceholderText("Value to paste")
        self.val_input.setStyleSheet(
            "background: #2d333a; border: 1px solid #454950;"
            "border-radius: 8px; padding: 6px; color: #ffffff;"
        )
        layout.addWidget(self.val_input)

        from clipbar.qt import QCheckBox
        self.lock_check = QCheckBox("Lock with password")
        self.lock_check.setStyleSheet("color: #dcddde; font-size: 12px;")
        layout.addWidget(self.lock_check)

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        add_btn = QPushButton("Add")
        add_btn.setDefault(True)
        add_btn.setStyleSheet(
            "background: #494e54; color: #ffffff; border: 1px solid #5c6066;"
            "border-radius: 10px; padding: 5px 14px; font-weight: 600;"
        )

        def do_add():
            v = self.val_input.text().strip()
            if v:
                # Stays open if the password prompt was cancelled.
                if self.on_add(self.title_input.text().strip(), v, self.lock_check.isChecked()) is not False:
                    self.accept()

        add_btn.clicked.connect(do_add)
        btn_box.addWidget(add_btn)
        layout.addLayout(btn_box)


class RenameDialog(QDialog):
    """Small dialog to name / rename a saved item."""

    def __init__(self, current_title: str, on_save: Callable[[str], None], parent=None):
        super().__init__(parent)
        self.on_save = on_save
        self.setWindowTitle("Title")
        self.setFixedSize(260, 140)
        self.setStyleSheet(CLIPBAR_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl = QLabel("Title")
        lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff;")
        layout.addWidget(lbl)

        self.title_input = QLineEdit(current_title)
        self.title_input.setPlaceholderText("e.g. Bank name")
        self.title_input.setStyleSheet(
            "background: #2d333a; border: 1px solid #454950;"
            "border-radius: 8px; padding: 6px; color: #ffffff;"
        )
        layout.addWidget(self.title_input)

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.setStyleSheet(
            "background: #494e54; color: #ffffff; border: 1px solid #5c6066;"
            "border-radius: 10px; padding: 5px 14px; font-weight: 600;"
        )
        save_btn.clicked.connect(lambda: (self.on_save(self.title_input.text().strip()), self.accept()))
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)


class ShortcutsDialog(QDialog):
    """Dialog displaying keyboard cheat sheet matching ShortcutsButton in Swift."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ClipBar Shortcuts")
        self.setFixedSize(320, 390)
        self.setStyleSheet(CLIPBAR_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("Keyboard Shortcuts")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffffff;")
        layout.addWidget(title)

        shortcuts = [
            ("↵", "Paste selected item"),
            ("Alt + ↵", "Copy without pasting"),
            ("Ctrl + 1–9", "Paste item 1–9"),
            ("↑  ↓", "Move selection"),
            ("Tab", "Next filter"),
            ("Ctrl + [", "Previous tab"),
            ("Ctrl + ]", "Next tab"),
            ("Ctrl + S", "Move to Saved"),
            ("Ctrl + P", "Pin or unpin"),
            ("Ctrl + E", "View and edit"),
            ("Ctrl + ⌫", "Delete"),
            ("Ctrl + ,", "Settings"),
            ("Esc", "Clear search / close"),
        ]

        from clipbar.qt import QGridLayout
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)

        for i, (key, desc) in enumerate(shortcuts):
            key_lbl = QLabel(key)
            key_lbl.setProperty("class", "KeyCap")
            key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(key_lbl, i, 0, Qt.AlignmentFlag.AlignRight)

            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("font-size: 12px; color: #dcddde;")
            grid.addWidget(desc_lbl, i, 1)

        layout.addLayout(grid)
        layout.addStretch()


class ClipView(QWidget):
    """Main floating panel window matching ClipView.swift (opaque Linux theme)."""

    MARGIN = 14
    PANEL_WIDTH = 400
    PANEL_HEIGHT = 540

    def __init__(
        self,
        store: ClipStore,
        on_paste: Callable[[ClipItem, bool], None],
        on_edit: Callable[[ClipItem], None],
        on_open_settings: Callable[[], None],
        on_close: Callable[[], None],
        parent=None
    ):
        super().__init__(parent)
        self.store = store
        self.on_paste_callback = on_paste
        self.on_edit_callback = on_edit
        self.on_open_settings_callback = on_open_settings
        self.on_close_callback = on_close

        self._confirming_clear = False
        self._clear_confirm_timer = QTimer(self)
        self._clear_confirm_timer.setSingleShot(True)
        self._clear_confirm_timer.timeout.connect(self._reset_clear_confirm)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        # Transparent margins keep the rounded floating-card silhouette.  The
        # card itself is opaque now (see styles.py THEME NOTE) — we no longer
        # rely on rgba translucency, only on this margin staying transparent.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(self.PANEL_WIDTH + self.MARGIN * 2, self.PANEL_HEIGHT + self.MARGIN * 2)

        self._init_ui()
        self.store.add_listener(self.on_store_updated)

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)

        self.container = QFrame()
        self.container.setObjectName("PanelContainer")
        self.container.setStyleSheet(CLIPBAR_QSS)

        panel_layout = QVBoxLayout(self.container)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(10)

        # 1. Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Mode Switch: History | Drafts | Saved
        self.mode_frame = QFrame()
        self.mode_frame.setObjectName("ModeSwitchFrame")
        mode_box = QHBoxLayout(self.mode_frame)
        mode_box.setContentsMargins(3, 3, 3, 3)
        mode_box.setSpacing(2)

        self.btn_history = QPushButton("History")
        self.btn_history.setProperty("class", "ModeButton")
        self.btn_history.setIcon(get_icon("history", "#ffffff"))
        self.btn_history.clicked.connect(lambda: self._set_mode("history"))
        mode_box.addWidget(self.btn_history)

        self.btn_drafts = QPushButton("Drafts")
        self.btn_drafts.setProperty("class", "ModeButton")
        self.btn_drafts.setIcon(get_icon("drafts", "#ffffff"))
        self.btn_drafts.clicked.connect(lambda: self._set_mode("drafts"))
        mode_box.addWidget(self.btn_drafts)

        self.btn_saved = QPushButton("Saved")
        self.btn_saved.setProperty("class", "ModeButton")
        self.btn_saved.setIcon(get_icon("saved", "#ffffff"))
        self.btn_saved.clicked.connect(lambda: self._set_mode("saved"))
        mode_box.addWidget(self.btn_saved)

        header_layout.addWidget(self.mode_frame)

        # Paused Button
        self.btn_paused = QPushButton("Paused")
        self.btn_paused.setObjectName("PausedButton")
        self.btn_paused.setToolTip("Not recording new copies. Click to resume.")
        self.btn_paused.clicked.connect(self._toggle_pause)
        header_layout.addWidget(self.btn_paused)

        header_layout.addStretch()

        # Add Saved Button (+)
        self.btn_add_saved = QPushButton()
        self.btn_add_saved.setProperty("class", "GlassIconButton")
        self.btn_add_saved.setIcon(get_icon("plus", "#ffffff"))
        self.btn_add_saved.setToolTip("Add a saved item")
        self.btn_add_saved.clicked.connect(self._show_add_saved)
        header_layout.addWidget(self.btn_add_saved)

        # Clear Confirm Button (Red)
        self.btn_clear_confirm = QPushButton("Clear")
        self.btn_clear_confirm.setObjectName("ClearConfirmButton")
        self.btn_clear_confirm.clicked.connect(self._do_clear)
        header_layout.addWidget(self.btn_clear_confirm)

        # Trash / Clear Toggle Button
        self.btn_trash = QPushButton()
        self.btn_trash.setProperty("class", "GlassIconButton")
        self.btn_trash.setIcon(get_icon("trash", "#ffffff"))
        self.btn_trash.clicked.connect(self._toggle_clear_confirm)
        header_layout.addWidget(self.btn_trash)

        # Settings Gear Button
        self.btn_settings = QPushButton()
        self.btn_settings.setProperty("class", "GlassIconButton")
        self.btn_settings.setIcon(get_icon("gear", "#ffffff"))
        self.btn_settings.setToolTip("Settings (Ctrl+,)")
        self.btn_settings.clicked.connect(self.on_open_settings_callback)
        header_layout.addWidget(self.btn_settings)

        panel_layout.addLayout(header_layout)

        # 2. Search Field
        self.search_frame = QFrame()
        self.search_frame.setObjectName("SearchFrame")
        search_box = QHBoxLayout(self.search_frame)
        search_box.setContentsMargins(8, 4, 8, 4)
        search_box.setSpacing(7)

        search_icon = QLabel()
        search_icon.setPixmap(get_icon("search", "#8a8e92").pixmap(14, 14))
        search_box.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("Search clipboard history")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_box.addWidget(self.search_input)

        self.btn_clear_search = QPushButton()
        self.btn_clear_search.setProperty("class", "GlassIconButton")
        self.btn_clear_search.setIcon(get_icon("close", "#8a8e92"))
        self.btn_clear_search.setFixedSize(18, 18)
        self.btn_clear_search.clicked.connect(lambda: self.search_input.setText(""))
        self.btn_clear_search.setVisible(False)
        search_box.addWidget(self.btn_clear_search)

        panel_layout.addWidget(self.search_frame)

        # 3. Filter Bar (History mode)
        self.filter_bar = QWidget()
        filter_layout = QHBoxLayout(self.filter_bar)
        filter_layout.setContentsMargins(2, 0, 2, 0)
        filter_layout.setSpacing(4)

        self.filter_buttons = {}
        for f in Filter:
            btn = QPushButton(f.value)
            btn.setProperty("class", "FilterChip")
            btn.clicked.connect(lambda checked, f_val=f: self._set_filter(f_val))
            filter_layout.addWidget(btn)
            self.filter_buttons[f] = btn

        filter_layout.addStretch()
        panel_layout.addWidget(self.filter_bar)

        # 4. Scroll Area for Rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; border: none; }")
        if self.scroll_area.viewport():
            self.scroll_area.viewport().setStyleSheet("background: transparent;")
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(2)
        self.list_layout.addStretch()
        self.scroll_area.setWidget(self.list_container)
        panel_layout.addWidget(self.scroll_area, 1)

        # 5. Access Banner (if paste permission / utility is missing)
        self.banner_frame = QFrame()
        self.banner_frame.setStyleSheet(
            "background: #37301f; border-radius: 10px; padding: 6px 10px;"
        )
        banner_layout = QHBoxLayout(self.banner_frame)
        banner_layout.setContentsMargins(6, 6, 6, 6)
        banner_lbl = QLabel("Install xdotool or wtype to paste into apps. Until then items are copied.")
        banner_lbl.setStyleSheet("color: #f59f00; font-size: 11px;")
        banner_layout.addWidget(banner_lbl)
        panel_layout.addWidget(self.banner_frame)

        # 6. Footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(6, 0, 6, 0)

        self.footer_status = QLabel("0 items")
        self.footer_status.setObjectName("FooterCount")
        footer_layout.addWidget(self.footer_status)

        footer_layout.addStretch()

        # "Paste" plus a key cap, flat until hovered, as in the Mac footer.
        self.btn_paste_action = QPushButton()
        self.btn_paste_action.setObjectName("PasteFooterButton")
        paste_layout = QHBoxLayout(self.btn_paste_action)
        paste_layout.setContentsMargins(12, 0, 5, 0)
        paste_layout.setSpacing(6)
        self.paste_label = QLabel("Paste")
        self.paste_label.setObjectName("PasteFooterLabel")
        paste_key = QLabel("↵")
        paste_key.setProperty("class", "KeyCap")
        paste_key.setFixedSize(18, 18)
        paste_key.setAlignment(Qt.AlignmentFlag.AlignCenter)
        paste_layout.addWidget(self.paste_label)
        paste_layout.addWidget(paste_key)
        self.btn_paste_action.setFixedHeight(28)
        self.btn_paste_action.setMinimumWidth(84)
        self.btn_paste_action.clicked.connect(self._on_footer_paste)
        footer_layout.addWidget(self.btn_paste_action)

        self.btn_shortcuts = QPushButton()
        self.btn_shortcuts.setProperty("class", "GlassIconButton")
        self.btn_shortcuts.setIcon(get_icon("keyboard", "#ced4da"))
        self.btn_shortcuts.setToolTip("Keyboard shortcuts")
        self.btn_shortcuts.clicked.connect(self._show_shortcuts)
        footer_layout.addWidget(self.btn_shortcuts)

        panel_layout.addLayout(footer_layout)
        root_layout.addWidget(self.container)

        self._update_view()

    # MARK: - State Management

    def _set_mode(self, mode: str):
        self.store.mode = mode
        self.search_input.setText("")
        self._update_view()

    def _set_filter(self, f: Filter):
        self.store.filter = f
        self._update_view()

    def _toggle_pause(self):
        self.store.paused = not self.store.paused
        self._update_view()

    def _toggle_clear_confirm(self):
        self._confirming_clear = not self._confirming_clear
        if self._confirming_clear:
            self._clear_confirm_timer.start(3000)
        else:
            self._clear_confirm_timer.stop()
        self._update_view()

    def _reset_clear_confirm(self):
        self._confirming_clear = False
        self._update_view()

    def _do_clear(self):
        if self.store.mode == "drafts":
            self.store.clear_drafts()
        else:
            self.store.clear(including_pinned=False)
        self._reset_clear_confirm()

    def _on_search_changed(self, text: str):
        self.store.query = text
        self.btn_clear_search.setVisible(bool(text))
        self._render_rows()

    def _show_add_saved(self):
        dlg = SavedItemDialog(on_add=self.store.add_saved, parent=self)
        dlg.exec()

    def _show_rename(self, item: ClipItem):
        dlg = RenameDialog(current_title=item.title or "", on_save=lambda t: self.store.rename_saved(item.id, t), parent=self)
        dlg.exec()

    def _show_shortcuts(self):
        dlg = ShortcutsDialog(self)
        dlg.exec()

    def _on_footer_paste(self):
        item = self.store.selected_item
        if item:
            self.on_paste_callback(item, True)

    def on_store_updated(self):
        self._update_view()

    def _update_view(self):
        settings = Settings.shared()

        # Mode buttons active state
        self.btn_history.setProperty("active", "true" if self.store.mode == "history" else "false")
        self.btn_drafts.setProperty("active", "true" if self.store.mode == "drafts" else "false")
        self.btn_saved.setProperty("active", "true" if self.store.mode == "saved" else "false")
        self.btn_drafts.setVisible(settings.drafts_enabled)

        # Style refresh
        self.btn_history.style().unpolish(self.btn_history)
        self.btn_history.style().polish(self.btn_history)
        self.btn_drafts.style().unpolish(self.btn_drafts)
        self.btn_drafts.style().polish(self.btn_drafts)
        self.btn_saved.style().unpolish(self.btn_saved)
        self.btn_saved.style().polish(self.btn_saved)

        # Paused Button
        self.btn_paused.setVisible(self.store.paused)

        # Header Right
        showing_saved = self.store.mode == "saved"
        self.btn_add_saved.setVisible(showing_saved)
        self.btn_trash.setVisible(not showing_saved)
        self.btn_clear_confirm.setVisible(not showing_saved and self._confirming_clear)
        if self._confirming_clear:
            self.btn_trash.setIcon(get_icon("close", "#ffffff"))
        else:
            self.btn_trash.setIcon(get_icon("trash", "#ffffff"))

        # Search placeholder
        if showing_saved:
            self.search_input.setPlaceholderText("Search saved items")
        elif self.store.mode == "drafts":
            self.search_input.setPlaceholderText("Search drafts")
        else:
            self.search_input.setPlaceholderText("Search clipboard history")

        # Filter bar
        self.filter_bar.setVisible(self.store.mode == "history")
        for f, btn in self.filter_buttons.items():
            btn.setProperty("active", "true" if self.store.filter == f else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Banner
        self.banner_frame.setVisible(settings.auto_paste and not Clipboard.can_paste())

        # Render list
        self._render_rows()

        # Footer
        if self.store.toast:
            self.footer_status.setText(f"✓  {self.store.toast}")
            self.footer_status.setStyleSheet("color: #51cf66; font-size: 11px; font-weight: 600;")
        else:
            total = len(self.store.saved) if showing_saved else (len(self.store.drafts) if self.store.mode == "drafts" else len(self.store.items))
            shown = len(self.store.visible)
            if shown != total:
                self.footer_status.setText(f"{shown} of {total}")
            elif self.store.mode == "drafts":
                self.footer_status.setText(f"{total} draft" if total == 1 else f"{total} drafts")
            else:
                self.footer_status.setText(f"{total} item" if total == 1 else f"{total} items")
            self.footer_status.setStyleSheet("color: #7f8287; font-size: 11px; font-weight: 500;")

        self.paste_label.setText("Paste" if settings.auto_paste else "Copy")

    def clear_rendered_rows(self):
        """Cleans up rendered row widgets to free RAM when panel is closed."""
        while self.list_layout.count() > 1:
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _render_rows(self):
        self.clear_rendered_rows()

        items = self.store.visible
        if not items:
            empty_lbl = QLabel()
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #7f8287; font-size: 13px; padding-top: 60px;")
            if self.store.query:
                empty_lbl.setText(f"No matches for “{self.store.query}”")
            elif self.store.mode == "saved":
                empty_lbl.setText("No saved items\n\nKeep things you paste again and again,\nlike a card number or student ID.")
            elif self.store.mode == "drafts":
                empty_lbl.setText("No drafts\n\nLonger text you type in other apps is kept here\nfor a while, in case it gets lost.")
            else:
                empty_lbl.setText(f"{self.store.filter.empty_info[0]}\n\nCopy something and it will show up here.")
            self.list_layout.insertWidget(0, empty_lbl)
            return

        has_pinned_section = (self.store.mode == "history" and self.store.filter == Filter.ALL and items[0].pinned)
        inserted_recent_header = False

        # Limit to 50 items for ultra-lightweight memory footprint
        MAX_ITEMS = 50
        rendered_items = items[:MAX_ITEMS]

        for i, item in enumerate(rendered_items):
            # Section headers
            if has_pinned_section:
                if i == 0:
                    hdr = QLabel("PINNED")
                    hdr.setProperty("class", "SectionHeader")
                    self.list_layout.insertWidget(self.list_layout.count() - 1, hdr)
                elif not item.pinned and not inserted_recent_header:
                    hdr = QLabel("RECENT")
                    hdr.setProperty("class", "SectionHeader")
                    self.list_layout.insertWidget(self.list_layout.count() - 1, hdr)
                    inserted_recent_header = True

            shortcut_num = (i + 1) if i < 9 else None
            is_selected = (item.id == self.store.selection)

            row = ClipRowWidget(
                item=item,
                shortcut_idx=shortcut_num,
                selected=is_selected,
                store=self.store,
                on_paste=self.on_paste_callback,
                on_edit=self.on_edit_callback,
                on_rename=self._show_rename,
                parent=self.list_container
            )
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)

        if len(items) > MAX_ITEMS:
            more_lbl = QLabel(f"… and {len(items) - MAX_ITEMS} more items. Type in search to find anything.")
            more_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            more_lbl.setStyleSheet("color: #686b71; font-size: 11px; padding: 10px;")
            self.list_layout.insertWidget(self.list_layout.count() - 1, more_lbl)

    # MARK: - Key Events

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        # Ctrl+1..9 instant paste
        if modifiers & Qt.KeyboardModifier.ControlModifier and Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            idx = key - Qt.Key.Key_1
            if idx < len(self.store.visible):
                self.on_paste_callback(self.store.visible[idx], True)
                return

        if key == Qt.Key.Key_Up:
            self.store.move_selection(-1)
            self._update_view()
            return
        elif key == Qt.Key.Key_Down:
            self.store.move_selection(1)
            self._update_view()
            return
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.store.selected_item:
                direct = not bool(modifiers & Qt.KeyboardModifier.AltModifier)
                self.on_paste_callback(self.store.selected_item, direct)
            return
        elif key == Qt.Key.Key_Escape:
            if self.search_input.text():
                self.search_input.setText("")
            else:
                self.on_close_callback()
            return
        elif key in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab) and self.store.mode == "history":
            # Qt reports Shift+Tab as Backtab.
            delta = -1 if key == Qt.Key.Key_Backtab or modifiers & Qt.KeyboardModifier.ShiftModifier else 1
            self.store.cycle_filter(delta)
            self._update_view()
            return
        elif modifiers & Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_BracketLeft:
                self._switch_mode_delta(-1)
                return
            elif key == Qt.Key.Key_BracketRight:
                self._switch_mode_delta(1)
                return
            elif key == Qt.Key.Key_S and self.store.mode != "saved":
                if self.store.selected_item:
                    self.store.save_item(self.store.selected_item)
                return
            elif key == Qt.Key.Key_P and self.store.mode == "history":
                if self.store.selected_item:
                    self.store.toggle_pin(self.store.selected_item)
                return
            elif key == Qt.Key.Key_E:
                if self.store.selected_item:
                    self.on_edit_callback(self.store.selected_item)
                return
            elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
                if self.store.selected_item:
                    self.store.remove(self.store.selected_item)
                return
            elif key == Qt.Key.Key_Comma:
                self.on_open_settings_callback()
                return

        super().keyPressEvent(event)

    def _switch_mode_delta(self, delta: int):
        modes = ["history", "drafts", "saved"] if Settings.shared().drafts_enabled else ["history", "saved"]
        curr = modes.index(self.store.mode) if self.store.mode in modes else 0
        new_mode = modes[max(0, min(len(modes) - 1, curr + delta))]
        self._set_mode(new_mode)
