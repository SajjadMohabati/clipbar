"""Editor and Inspector window matching EditorView.swift."""

from __future__ import annotations
import os
import subprocess
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from clipbar.clipboard import Clipboard, Icons, ImageStore
from clipbar.qt import (
    QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QScrollArea, QMenu, QFileDialog, QCheckBox,
    QLineEdit, QColor, QPixmap, QPainter, QPainterPath, QPen, QBrush,
    QIcon, Qt, QSplitter
)
from clipbar.store import ClipItem, ClipStore
from clipbar.styles import LIQUID_GLASS_QSS, get_icon, switch_qss
from clipbar.transforms import TextTransform


def is_rtl(text: str) -> bool:
    """Checks if text begins with a Right-to-Left script (Persian, Arabic, Hebrew)."""
    for char in text[:400]:
        cp = ord(char)
        if 0x0590 <= cp <= 0x08FF or 0xFB1D <= cp <= 0xFDFF or 0xFE70 <= cp <= 0xFEFF:
            return True
    return False


class EditorView(QMainWindow):
    """Full viewer, editor, and inspector window matching EditorView.swift."""

    def __init__(
        self,
        store: ClipStore,
        item: ClipItem,
        on_paste: Callable[[ClipItem], None],
        on_close: Callable[[], None],
        parent=None
    ):
        super().__init__(parent)
        self.store = store
        self.item = item
        self.on_paste_callback = on_paste
        self.on_close_callback = on_close

        # Working state
        self._draft_text = item.text
        self._saved_title = item.title or ""
        self._locked = item.is_locked
        self._baseline = (item.text, item.title or "", item.is_locked)
        self._actual_size = False
        self._recognizing = False

        self.setWindowTitle(f"ClipBar — {self._get_title()}")
        self.resize(900, 600)
        self.setStyleSheet(LIQUID_GLASS_QSS + switch_qss())

        self._init_ui()

    @property
    def is_text(self) -> bool:
        return self.item.kind in ("text", "link", "color")

    @property
    def is_saved(self) -> bool:
        return self.store.is_saved(self.item)

    @property
    def dirty(self) -> bool:
        title_changed = self.is_saved and self._saved_title != self._baseline[1]
        if not self.is_text:
            return title_changed
        return (
            self._draft_text != self._baseline[0]
            or title_changed
            or (self.is_saved and self._locked != self._baseline[2])
        )

    def _get_title(self) -> str:
        k = self.item.kind
        if k == "text":
            return "Text"
        if k == "link":
            return "Link"
        if k == "color":
            return "Color"
        if k == "image":
            return "Image"
        if k == "files":
            count = len(self.item.files or [])
            return "File" if count == 1 else f"{count} Files"
        return "Item"

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("EditorToolbar")
        toolbar.setStyleSheet("QFrame#EditorToolbar { background: rgba(30, 36, 46, 0.95); border-bottom: 1px solid rgba(255, 255, 255, 0.12); }")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 6, 12, 6)
        tb_layout.setSpacing(8)

        # Title
        lbl_type = QLabel(self._get_title())
        lbl_type.setStyleSheet("font-size: 15px; font-weight: 600; color: #ffffff;")
        tb_layout.addWidget(lbl_type)
        tb_layout.addStretch()

        # Text Transforms Menu
        if self.is_text:
            btn_transform = QPushButton("Transform")
            btn_transform.setProperty("class", "GlassIconButton")
            btn_transform.setIcon(get_icon("wand", "#ced4da"))
            btn_transform.setStyleSheet(
                "background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);"
                "border-radius: 8px; padding: 5px 10px; color: #ffffff; font-size: 12px;"
            )
            transform_menu = QMenu(self)
            for group in TextTransform.groups():
                for trans in group:
                    act = transform_menu.addAction(trans.value)
                    act.triggered.connect(lambda checked, t=trans: self._apply_transform(t))
                transform_menu.addSeparator()
            btn_transform.setMenu(transform_menu)
            tb_layout.addWidget(btn_transform)

        # Pin / Unpin
        if not self.store.is_draft(self.item):
            self.btn_pin = QPushButton("Unpin" if self.item.pinned else "Pin")
            self.btn_pin.setProperty("class", "GlassIconButton")
            self.btn_pin.setIcon(get_icon("pin_fill" if self.item.pinned else "pin", "#ced4da"))
            self.btn_pin.clicked.connect(self._toggle_pin)
            tb_layout.addWidget(self.btn_pin)

        # Move to Saved / Move to History
        if self.is_saved:
            if not self.item.is_locked:
                btn_unsave = QPushButton("Move to History")
                btn_unsave.setProperty("class", "GlassIconButton")
                btn_unsave.setIcon(get_icon("history", "#ced4da"))
                btn_unsave.clicked.connect(lambda: (self.store.unsave(self.item), self.close()))
                tb_layout.addWidget(btn_unsave)
        else:
            btn_save = QPushButton("Move to Saved")
            btn_save.setProperty("class", "GlassIconButton")
            btn_save.setIcon(get_icon("bookmark", "#ced4da"))
            btn_save.clicked.connect(lambda: (self.store.save_item(self.item), self.close()))
            tb_layout.addWidget(btn_save)

        # Copy button (Ctrl+Shift+C)
        btn_copy = QPushButton("Copy")
        btn_copy.setProperty("class", "GlassIconButton")
        btn_copy.setIcon(get_icon("copy", "#ced4da"))
        btn_copy.clicked.connect(self._do_copy)
        tb_layout.addWidget(btn_copy)

        # Delete button
        btn_delete = QPushButton("Delete")
        btn_delete.setProperty("class", "GlassIconButton")
        btn_delete.setIcon(get_icon("trash", "#fa5252"))
        btn_delete.setStyleSheet("color: #ff6b6b;")
        btn_delete.clicked.connect(lambda: (self.store.remove(self.item), self.close()))
        tb_layout.addWidget(btn_delete)

        # Paste button
        btn_paste = QPushButton("Paste ↵")
        btn_paste.setStyleSheet(
            "background: rgba(64, 150, 255, 0.85); color: #ffffff; border: none;"
            "border-radius: 8px; padding: 6px 14px; font-weight: 600;"
        )
        btn_paste.clicked.connect(self._do_paste)
        tb_layout.addWidget(btn_paste)

        main_layout.addWidget(toolbar)

        # 2. Main Content Splitter (Left: Editor, Right: Inspector)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: rgba(255, 255, 255, 0.1); width: 1px; }")

        # Left: Content
        left_widget = self._create_content_widget()
        splitter.addWidget(left_widget)

        # Right: Inspector
        right_widget = self._create_inspector_widget()
        right_widget.setFixedWidth(270)
        splitter.addWidget(right_widget)

        main_layout.addWidget(splitter, 1)

        # 3. Bottom Bar
        bottom_bar = QFrame()
        bottom_bar.setObjectName("EditorBottomBar")
        bottom_bar.setStyleSheet("QFrame#EditorBottomBar { background: rgba(30, 36, 46, 0.95); border-top: 1px solid rgba(255, 255, 255, 0.12); }")
        bb_layout = QHBoxLayout(bottom_bar)
        bb_layout.setContentsMargins(16, 8, 16, 8)

        self.lbl_dirty = QLabel("Edit the text, then press Save.")
        self.lbl_dirty.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 12px;")
        bb_layout.addWidget(self.lbl_dirty)
        bb_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet(
            "background: rgba(255, 255, 255, 0.1); color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.16);"
            "border-radius: 8px; padding: 6px 14px;"
        )
        self.btn_cancel.clicked.connect(self.close)
        bb_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Save")
        self.btn_save.setToolTip("Save and close (Ctrl+S)")
        self.btn_save.setStyleSheet(
            "background: rgba(64, 150, 255, 0.85); color: #ffffff; border: none;"
            "border-radius: 8px; padding: 6px 18px; font-weight: 600;"
        )
        self.btn_save.clicked.connect(self._do_save)
        bb_layout.addWidget(self.btn_save)

        self.btn_done = QPushButton("Done")
        self.btn_done.setStyleSheet(
            "background: rgba(64, 150, 255, 0.85); color: #ffffff; border: none;"
            "border-radius: 8px; padding: 6px 18px; font-weight: 600;"
        )
        self.btn_done.clicked.connect(self.close)
        bb_layout.addWidget(self.btn_done)

        main_layout.addWidget(bottom_bar)
        self._update_dirty_status()

    def _create_content_widget(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        if self.item.kind in ("text", "link", "color"):
            self.text_editor = QTextEdit()
            self.text_editor.setText(self._draft_text)
            self.text_editor.setStyleSheet(
                "background: rgba(20, 24, 32, 0.95); border: none; padding: 16px; color: #ffffff;"
                "font-size: 14px; line-height: 1.5; selection-background-color: rgba(64, 150, 255, 0.6);"
            )
            # RTL layout detection for Persian, Arabic, Hebrew
            if is_rtl(self._draft_text):
                self.text_editor.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            else:
                self.text_editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

            self.text_editor.textChanged.connect(self._on_text_edited)
            layout.addWidget(self.text_editor)

        elif self.item.kind == "image" and self.item.image:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("background: rgba(18, 22, 28, 0.95); border: none;")

            img_container = QWidget()
            img_layout = QVBoxLayout(img_container)
            img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.img_label = QLabel()
            self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_path = ImageStore.url(self.item.image)
            if img_path.exists():
                pix = QPixmap(str(img_path))
                scaled = pix.scaled(600, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.img_label.setPixmap(scaled)

            img_layout.addWidget(self.img_label)
            scroll.setWidget(img_container)
            layout.addWidget(scroll)

        elif self.item.kind == "files" and self.item.files:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            files_box = QWidget()
            f_layout = QVBoxLayout(files_box)
            f_layout.setContentsMargins(16, 16, 16, 16)
            f_layout.setSpacing(8)

            for fp in self.item.files:
                row = QFrame()
                row.setStyleSheet("background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 8px;")
                r_box = QHBoxLayout(row)
                icon_lbl = QLabel()
                icon = Icons.file_icon(fp)
                if icon:
                    icon_lbl.setPixmap(icon.pixmap(24, 24))
                r_box.addWidget(icon_lbl)

                info_box = QVBoxLayout()
                p = Path(fp)
                name_lbl = QLabel(p.name)
                name_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #ffffff;")
                path_lbl = QLabel(fp)
                path_lbl.setStyleSheet("font-size: 11px; color: rgba(255, 255, 255, 0.5);")
                info_box.addWidget(name_lbl)
                info_box.addWidget(path_lbl)
                r_box.addLayout(info_box, 1)

                btn_open = QPushButton("Show in File Manager")
                btn_open.setStyleSheet("background: rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 4px 8px; color: #ffffff; font-size: 11px;")
                btn_open.clicked.connect(lambda checked, pth=fp: subprocess.Popen(["xdg-open", str(Path(pth).parent)]))
                r_box.addWidget(btn_open)

                f_layout.addWidget(row)

            f_layout.addStretch()
            scroll.setWidget(files_box)
            layout.addWidget(scroll)

        return container

    def _create_inspector_widget(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("Inspector")
        scroll.setStyleSheet("QScrollArea#Inspector, QScrollArea#Inspector > QWidget > QWidget { background: rgba(26, 32, 42, 0.95); border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(16)

        # Saved item section
        if self.is_saved:
            sec_saved = self._create_section("SAVED ITEM")
            s_layout = QVBoxLayout(sec_saved)
            s_layout.setSpacing(8)

            self.saved_title_input = QLineEdit(self._saved_title)
            self.saved_title_input.setPlaceholderText("Title, e.g. Bank name")
            self.saved_title_input.setStyleSheet(
                "background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15);"
                "border-radius: 6px; padding: 6px; color: #ffffff; font-size: 12px;"
            )
            self.saved_title_input.textChanged.connect(self._on_title_edited)
            s_layout.addWidget(self.saved_title_input)

            if self.is_text:
                self.check_locked = QCheckBox("Lock with password")
                self.check_locked.setChecked(self._locked)
                self.check_locked.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 11px;")
                self.check_locked.toggled.connect(self._on_locked_toggled)
                s_layout.addWidget(self.check_locked)

            self._add_section(layout, sec_saved)

        # Color Inspector
        if self.item.kind == "color" and self.item.color:
            sec_color = self._create_section("COLOR")
            c_layout = QVBoxLayout(sec_color)
            swatch = QFrame()
            swatch.setFixedHeight(60)
            swatch.setStyleSheet(f"background: {self.item.color}; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);")
            c_layout.addWidget(swatch)

            hex_row = self._create_info_row("HEX", self.item.color)
            c_layout.addLayout(hex_row)
            self._add_section(layout, sec_color)

        # Details section
        sec_details = self._create_section("DETAILS")
        d_layout = QVBoxLayout(sec_details)
        d_layout.setSpacing(6)
        d_layout.addLayout(self._create_info_row("Type", self._get_title()))
        if self.item.source:
            d_layout.addLayout(self._create_info_row("Copied from", self.item.source.capitalize()))
        d_layout.addLayout(self._create_info_row("Copied", self.item.date.strftime("%b %d, %H:%M")))
        d_layout.addLayout(self._create_info_row("Used", f"{self.item.uses} times" if self.item.uses != 1 else "Once"))

        if self.is_text:
            text = self._draft_text
            chars = len(text)
            words = len(text.split())
            lines = text.count("\n") + 1
            d_layout.addLayout(self._create_info_row("Characters", str(chars)))
            d_layout.addLayout(self._create_info_row("Words", str(words)))
            d_layout.addLayout(self._create_info_row("Lines", str(lines)))

        self._add_section(layout, sec_details)

        # OCR & Image text
        if self.item.kind == "image" and self.item.image:
            sec_ocr = self._create_section("TEXT IN IMAGE")
            o_layout = QVBoxLayout(sec_ocr)
            if self.item.text:
                lbl_ocr = QLabel(self.item.text[:200])
                lbl_ocr.setWordWrap(True)
                lbl_ocr.setStyleSheet("font-size: 11px; color: rgba(255, 255, 255, 0.7);")
                o_layout.addWidget(lbl_ocr)

                btn_copy_ocr = QPushButton("Copy Text")
                btn_copy_ocr.setStyleSheet("background: rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 4px; color: #ffffff;")
                btn_copy_ocr.clicked.connect(lambda: Clipboard.write(self.item.text))
                o_layout.addWidget(btn_copy_ocr)
            else:
                btn_do_ocr = QPushButton("Recognize Text (OCR)")
                btn_do_ocr.setStyleSheet("background: rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 4px; color: #ffffff;")
                btn_do_ocr.clicked.connect(self._run_ocr)
                o_layout.addWidget(btn_do_ocr)

            btn_save_img = QPushButton("Save Image…")
            btn_save_img.setStyleSheet("background: rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 4px; color: #ffffff;")
            btn_save_img.clicked.connect(self._save_image_as)
            o_layout.addWidget(btn_save_img)

            self._add_section(layout, sec_ocr)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _create_section(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("InspectorSection")
        frame.setProperty("sectionTitle", title.title())
        frame.setStyleSheet(
            "QFrame#InspectorSection { background: rgba(255, 255, 255, 0.04);"
            "border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; }"
        )
        return frame

    def _add_section(self, layout, frame: QFrame) -> None:
        """A section title above its rounded box, like the Mac inspector."""
        title = QLabel(frame.property("sectionTitle"))
        title.setStyleSheet("color: rgba(255, 255, 255, 0.55); font-size: 11px; font-weight: 600; padding-left: 2px;")
        group = QVBoxLayout()
        group.setSpacing(6)
        group.addWidget(title)
        group.addWidget(frame)
        layout.addLayout(group)

    def _create_info_row(self, label: str, val: str) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 12px;")
        val_lbl = QLabel(val)
        val_lbl.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500;")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val_lbl)
        return row

    def keyPressEvent(self, event):
        # Esc is Done (or Cancel), Ctrl+S saves and closes, as on the Mac.
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._do_save()
        else:
            super().keyPressEvent(event)

    def _on_text_edited(self):
        self._draft_text = self.text_editor.toPlainText()
        self._update_dirty_status()

    def _on_title_edited(self, text: str):
        self._saved_title = text
        self._update_dirty_status()

    def _on_locked_toggled(self, checked: bool):
        self._locked = checked
        self._update_dirty_status()

    def _update_dirty_status(self):
        dirty = self.dirty
        if dirty:
            self.lbl_dirty.setText("● Unsaved changes")
            self.lbl_dirty.setStyleSheet("color: #f59f00; font-size: 12px; font-weight: 600;")
        else:
            self.lbl_dirty.setText("Edit the text, then press Save." if self.is_text else "")
            self.lbl_dirty.setStyleSheet("color: rgba(255, 255, 255, 0.4); font-size: 12px;")
        self.btn_cancel.setVisible(dirty)
        self.btn_save.setVisible(dirty)
        self.btn_done.setVisible(not dirty)

    def _toggle_pin(self):
        self.store.toggle_pin(self.item)
        self.btn_pin.setText("Unpin" if self.item.pinned else "Pin")
        self.btn_pin.setIcon(get_icon("pin_fill" if self.item.pinned else "pin", "#ced4da"))

    def _apply_transform(self, t: TextTransform):
        res = t.apply(self._draft_text)
        if res is not None:
            self.text_editor.setText(res)
            self._draft_text = res
            self._update_dirty_status()

    def _run_ocr(self):
        if not self.item.image:
            return
        text = ImageStore.recognize_text(self.item.image)
        if text:
            self.item.text = text
            self.store.update_text(self.item.id, text)
            self.store.save()
            self.close()

    def _save_image_as(self):
        if not self.item.image:
            return
        src = ImageStore.url(self.item.image)
        dest, _ = QFileDialog.getSaveFileName(self, "Save Image", "Clipboard Image.png", "Images (*.png)")
        if dest:
            try:
                import shutil
                shutil.copyfile(src, dest)
            except Exception:
                pass

    def _do_copy(self):
        item_to_copy = ClipItem.from_dict(self.item.to_dict())
        if self.is_text:
            item_to_copy.text = self._draft_text
        self.store.copy(item_to_copy)

    def _do_paste(self):
        item_to_paste = ClipItem.from_dict(self.item.to_dict())
        if self.is_text:
            item_to_paste.text = self._draft_text
        self.close()
        self.on_paste_callback(item_to_paste)

    def _do_save(self):
        if not self.dirty:
            self.close()
            return
        if self.is_saved:
            if not self.store.update_saved(self.item.id, title=self._saved_title, text=self._draft_text, locked=self._locked):
                return  # the password prompt was cancelled; keep the edits open
        elif self.is_text:
            self.store.update_text(self.item.id, self._draft_text)
        self.close()
