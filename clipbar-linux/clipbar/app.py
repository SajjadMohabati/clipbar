"""Application controller and tray manager matching App.swift."""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Optional

from clipbar.clipboard import Clipboard
from clipbar.clip_view import ClipView
from clipbar.draft_watcher import DraftWatcher
from clipbar.editor_view import EditorView
from clipbar.hotkey import HotKey
from clipbar import main_thread
from clipbar.qt import (
    QApplication, QSystemTrayIcon, QMenu, QIcon, QTimer,
    QCursor, QPoint, QRect, Qt
)
from clipbar.screenshot_watcher import ScreenshotWatcher
from clipbar.settings import Settings
from clipbar.settings_view import SettingsView
from clipbar.store import ClipItem, ClipStore
from clipbar.styles import get_icon


class ClipBarApp:
    """Main application controller managing Tray, Panel, Editor, and Settings."""

    def __init__(self, qapp: QApplication) -> None:
        self.qapp = qapp
        self.store = ClipStore()
        self.settings = Settings.shared()

        self.panel: Optional[ClipView] = None
        self.editor_window: Optional[EditorView] = None
        self.settings_window: Optional[SettingsView] = None

        self.draft_watcher = DraftWatcher(self.store)
        self.screenshot_watcher = ScreenshotWatcher(self._on_screenshot_captured)

        self._asked_for_paste_perm = False

    def launch(self) -> None:
        main_thread.install()
        self.store.load()

        self._setup_tray()
        self._setup_panel()

        # Global HotKey
        HotKey.shared().install(self.toggle_panel)
        HotKey.shared().register(self.settings.shortcut)

        # Watchers
        if self.settings.drafts_enabled:
            self.draft_watcher.start()
        if self.settings.capture_screenshots:
            self.screenshot_watcher.start()

        # Listen for setting changes
        self.settings.add_listener(self._on_setting_changed)

        self._last_img_cache_key = None

        # Clipboard monitoring: purely event-driven via QClipboard.dataChanged
        cb = self.qapp.clipboard()
        if cb:
            try:
                cb.dataChanged.connect(self._on_clipboard_data_changed)
            except Exception:
                pass

        # Fallback check timer with low frequency (2.5s) to catch any edge cases with minimal CPU
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self._poll_clipboard)
        self.clipboard_timer.start(500)

        # Handle focus lost on panel (close when clicking outside)
        self.qapp.focusChanged.connect(self._on_focus_changed)

    def _setup_tray(self) -> None:
        self.tray = QSystemTrayIcon(self.qapp)
        icon = get_icon("clipboard", "#ffffff")
        if icon:
            self.tray.setIcon(icon)
        app_icon = Path(__file__).resolve().parent.parent / "resources" / "clipbar.png"
        if app_icon.exists():
            self.qapp.setWindowIcon(QIcon(str(app_icon)))
        self.tray.setToolTip("ClipBar — Clipboard Manager")

        # Tray Menu
        self.tray_menu = QMenu()
        self.act_toggle = self.tray_menu.addAction("Open ClipBar")
        self.act_toggle.triggered.connect(self.toggle_panel)

        self.act_pause = self.tray_menu.addAction("Pause Capturing")
        self.act_pause.triggered.connect(self._toggle_pause)

        self.tray_menu.addSeparator()

        self.act_settings = self.tray_menu.addAction("Settings…")
        self.act_settings.triggered.connect(self.open_settings)

        self.tray_menu.addSeparator()

        self.act_quit = self.tray_menu.addAction("Quit ClipBar")
        self.act_quit.triggered.connect(self.quit)

        # IMPORTANT: do NOT call setContextMenu here.  On Linux a tray icon that
        # has a context menu shows that menu on a plain left-click (the desktop
        # never emits the "Trigger" activation), which forced users to click an
        # extra "Open ClipBar" item.  Leaving the menu unset makes a left-click
        # arrive as ActivationReason.Trigger so the panel opens directly, while
        # right-click arrives as ActivationReason.Context and we pop the same
        # menu ourselves (see _on_tray_activated).
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _setup_panel(self) -> None:
        self.panel = ClipView(
            store=self.store,
            on_paste=self.paste,
            on_edit=self.show_editor,
            on_open_settings=self.open_settings,
            on_close=self.hide_panel
        )

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        # Left-click opens the clipboard panel directly.  Right-click shows the
        # tray menu (Settings, Quit, ...) since no context menu is attached.
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_panel()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            self.tray_menu.popup(QCursor.pos())

    def toggle_panel(self) -> None:
        if self.panel and self.panel.isVisible():
            self.hide_panel()
        else:
            self.show_panel()

    def show_panel(self) -> None:
        if not self.panel:
            return
        self.store.prepare_for_display()
        self.panel.on_store_updated()
        self._position_panel()
        self.panel.show()
        self.panel.raise_()
        self.panel.activateWindow()

    def hide_panel(self) -> None:
        if self.panel:
            self.panel.hide()
            self.panel.clear_rendered_rows()
            import gc
            gc.collect()

    def _position_panel(self) -> None:
        """Positions panel neatly below the tray icon or top-right of active screen."""
        screen = self.qapp.primaryScreen()
        if not screen:
            return
        screen_geo = screen.availableGeometry()

        tray_geo = self.tray.geometry()
        p_w = self.panel.width()
        p_h = self.panel.height()

        if tray_geo.isValid() and tray_geo.x() > 0:
            x = tray_geo.x() - p_w // 2
            y = tray_geo.y() + tray_geo.height() + 4
        else:
            # Fallback: top right corner with padding
            x = screen_geo.x() + screen_geo.width() - p_w - 20
            y = screen_geo.y() + 32

        # Clamp inside screen boundaries
        x = max(screen_geo.left() + 10, min(x, screen_geo.right() - p_w - 10))
        y = max(screen_geo.top() + 10, min(y, screen_geo.bottom() - p_h - 10))

        self.panel.move(x, y)

    def _on_focus_changed(self, old_widget, new_widget) -> None:
        pass

    def paste(self, item: ClipItem, direct: bool = True) -> None:
        """Copies item and, if allowed, pastes directly into the target app."""
        self.hide_panel()
        # The password prompt and the clipboard both belong to the GUI thread.
        ready = self.store.unlocked(item)
        if not ready:
            return
        self.store.copy(ready)

        if not direct or not self.settings.auto_paste or not Clipboard.can_paste():
            return

        # Unregister the hotkey so the synthetic Ctrl+V can't trigger it, and give the
        # previous window a moment to take focus back; timers keep the UI responsive.
        HotKey.shared().unregister()

        def press():
            Clipboard.press_paste()
            QTimer.singleShot(150, lambda: HotKey.shared().register(self.settings.shortcut))

        QTimer.singleShot(80, press)

    def show_editor(self, item: ClipItem) -> None:
        self.hide_panel()
        ready = self.store.unlocked(item)
        if not ready:
            return

        def _on_editor_close():
            if self.editor_window:
                self.editor_window.close()
                self.editor_window = None
                import gc
                gc.collect()

        self.editor_window = EditorView(
            store=self.store,
            item=ready,
            on_paste=lambda it: self.paste(it, direct=True),
            on_close=_on_editor_close
        )
        self.editor_window.show()
        self.editor_window.raise_()
        self.editor_window.activateWindow()

    def open_settings(self) -> None:
        self.hide_panel()
        if not self.settings_window:
            self.settings_window = SettingsView(self.store)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _toggle_pause(self) -> None:
        self.store.paused = not self.store.paused
        self.act_pause.setText("Resume Capturing" if self.store.paused else "Pause Capturing")

    def _on_screenshot_captured(self, path) -> None:
        # Called from the watcher's thread.
        main_thread.run_on_main(lambda: self.store.add_screenshot(path, copy_to_clipboard=self.settings.copy_screenshots))

    def _on_clipboard_data_changed(self) -> None:
        self._poll_clipboard()

    def _poll_clipboard(self) -> None:
        cb = self.qapp.clipboard()
        if not cb:
            return
        mime_data = cb.mimeData()
        if not mime_data:
            return

        formats = list(mime_data.formats()) if hasattr(mime_data, "formats") else []
        text = mime_data.text() if mime_data.hasText() else None
        files = None
        if mime_data.hasUrls():
            files = [u.toLocalFile() for u in mime_data.urls() if u.isLocalFile()]

        img_data = None
        if mime_data.hasImage() and not files:
            img = cb.image()
            if not img.isNull():
                img_key = getattr(img, "cacheKey", lambda: None)()
                if img_key is None or img_key != self._last_img_cache_key:
                    from clipbar.qt import QByteArray, QBuffer
                    ba = QByteArray()
                    buf = QBuffer(ba)
                    buf.open(QBuffer.OpenModeFlag.WriteOnly)
                    img.save(buf, "PNG")
                    img_data = bytes(ba.data())
                    self._last_img_cache_key = img_key
            else:
                self._last_img_cache_key = None
        else:
            self._last_img_cache_key = None

        self.store.poll_clipboard(
            text=text,
            files=files,
            image_data=img_data,
            source=None,
            mime_types=formats
        )

    def _on_setting_changed(self, key: str, value) -> None:
        if key == "draftsEnabled":
            if value:
                self.draft_watcher.start()
            else:
                self.draft_watcher.stop()
        elif key == "captureScreenshots":
            if value:
                self.screenshot_watcher.start()
            else:
                self.screenshot_watcher.stop()
        elif key == "shortcut":
            HotKey.shared().register(value)
        elif key in ("keepDays", "maxItems", "cleanPinned"):
            self.store.apply_limits()

    def quit(self) -> None:
        self.store.save()
        self.draft_watcher.stop()
        self.screenshot_watcher.stop()
        HotKey.shared().unregister()
        self.qapp.quit()
