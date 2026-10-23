"""Draft watcher for recovering lost typed text, matching DraftWatcher.swift."""

from __future__ import annotations
import os
from typing import Optional, Set

from clipbar.clipboard import Clipboard
from clipbar.settings import Settings
from clipbar.store import ClipStore

try:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi
    _ATSPI_AVAILABLE = True
except (ImportError, ValueError):
    Atspi = None
    _ATSPI_AVAILABLE = False


def continues(text: str, earlier: str) -> bool:
    """Whether `text` is `earlier` with more typed or edited: they share most of their beginning."""
    shorter = min(len(text), len(earlier))
    if shorter == 0:
        return False
    return len(os.path.commonprefix([text, earlier])) * 10 >= shorter * 7


class DraftWatcher:
    """Keeps a copy of what you're typing in other apps, through Linux Accessibility (AT-SPI).

    Once a second it asks for the text of the focused field. It never listens to the keyboard
    and never reads password fields, search fields, terminals or password managers. Apps are
    identified through AT-SPI and /proc, which works the same on X11 and Wayland; when an app
    can't be identified, it is skipped.
    """

    MAX_LENGTH = 20_000
    # How long a slow or hung app may take to answer, in milliseconds.
    TIMEOUT_MS = 250
    # Terminals expose their whole scrollback as text; password managers are private.
    SKIPPED_APPS: Set[str] = {
        "terminal", "konsole", "alacritty", "kitty", "foot", "wezterm", "xterm", "urxvt",
        "rxvt", "tilix", "terminator", "ptyxis", "guake", "yakuake", "terminology", "sakura",
        "qterminal", "ghostty", "blackbox", "warp", "tabby", "contour", "st-256color",
        "1password", "bitwarden", "keepass", "seahorse", "kwalletmanager", "gopass", "qtpass",
        "enpass", "lastpass", "dashlane", "nordpass", "proton pass", "secrets", "passwords",
    }
    TEXT_ROLES = {"ENTRY", "TEXT", "PARAGRAPH", "DOCUMENT_TEXT", "SECTION", "COMBO_BOX"}

    def __init__(self, store: ClipStore) -> None:
        self.store = store
        self._timer = None
        self._listener = None
        self._focused = None
        self._seen_focus_event = False
        self._names = ""

        # The field being typed in, and the draft that belongs to it.
        self._field = None
        self._draft: Optional[str] = None
        self._last = ""
        self._peak = 0

    @staticmethod
    def is_available() -> bool:
        return _ATSPI_AVAILABLE

    def start(self) -> None:
        if self._timer is not None or not _ATSPI_AVAILABLE:
            return
        from clipbar.qt import QTimer
        try:
            Atspi.init()
            Atspi.set_timeout(self.TIMEOUT_MS, 5000)
            self._enable_accessibility()
            # Focus events arrive through the GLib main loop that Qt runs on Linux.
            self._listener = Atspi.EventListener.new(self._on_focus)
            self._listener.register("object:state-changed:focused")
        except Exception:
            self._listener = None
        # Everything runs on the GUI thread, like the Mac version, so nothing races the store.
        self._timer = QTimer()
        self._timer.timeout.connect(self.check)
        self._timer.start(1000)

    def stop(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        if self._listener is not None:
            try:
                self._listener.deregister("object:state-changed:focused")
            except Exception:
                pass
            self._listener = None
        self._focused = None
        self._forget()

    def _forget(self) -> None:
        self._field = None
        self._draft = None
        self._last = ""
        self._peak = 0

    @staticmethod
    def _enable_accessibility() -> None:
        """Most apps only expose their text to Accessibility once an assistive app asks."""
        try:
            from gi.repository import Gio, GLib
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            bus.call_sync(
                "org.a11y.Bus", "/org/a11y/bus", "org.freedesktop.DBus.Properties", "Set",
                GLib.Variant("(ssv)", ("org.a11y.Status", "IsEnabled", GLib.Variant("b", True))),
                None, Gio.DBusCallFlags.NONE, 1000, None,
            )
        except Exception:
            pass

    def _on_focus(self, event) -> None:
        self._seen_focus_event = True
        if event.detail1:
            self._focused = event.source

    # MARK: - Checking

    def check(self) -> None:
        settings = Settings.shared()
        if self.store.paused or not settings.drafts_enabled:
            return self._forget()
        element = self._focused_element()
        # No focused element usually means a menu or dialog is in the way; keep the session.
        if element is None:
            return
        app = self._app_name(element)
        if app is None or self._is_skipped(element, app):
            return self._forget()
        text = self._text(element)
        if text is None:
            return self._forget()

        if self._field is not element:
            # Web apps hand out a new element for the same field now and then;
            # if the text carries on from what was there, it's still the same message.
            if self._last and continues(text, self._last):
                self._field = element
                return
            # A different field: whatever is already in it isn't something being typed now.
            self._forget()
            self._field = element
            self._last = text
            self._peak = len(text)
            return
        if text == self._last:
            return
        self._last = text

        # Sent, cleared or wiped: the draft keeps the full text, and what follows is a new one.
        if len(text) * 2 < self._peak:
            self._draft = None
            self._peak = len(text)
        self._peak = max(self._peak, len(text))

        typed = text.strip()
        if len(typed) < settings.draft_min_length:
            return
        if settings.skip_sensitive and Clipboard.looks_sensitive(typed):
            return
        self._draft = self.store.record_draft(self._draft, text=typed, source=app)

    def _focused_element(self):
        element = self._focused
        if element is not None:
            try:
                if element.get_state_set().contains(Atspi.StateType.FOCUSED):
                    return element
            except Exception:
                pass
            self._focused = None
            return None
        if self._seen_focus_event:
            return None
        # Before the first focus event, look for the focused field in the active window.
        return self._search_focused()

    def _search_focused(self, budget: int = 400):
        try:
            desktop = Atspi.get_desktop(0)
            windows = []
            for i in range(desktop.get_child_count()):
                app = desktop.get_child_at_index(i)
                for j in range(app.get_child_count() if app else 0):
                    win = app.get_child_at_index(j)
                    if win and win.get_state_set().contains(Atspi.StateType.ACTIVE):
                        windows.append(win)
            queue = windows
            while queue and budget > 0:
                obj = queue.pop(0)
                budget -= 1
                states = obj.get_state_set()
                if states.contains(Atspi.StateType.FOCUSED):
                    return obj
                if not states.contains(Atspi.StateType.SHOWING) and obj not in windows:
                    continue
                for k in range(min(obj.get_child_count(), 200)):
                    child = obj.get_child_at_index(k)
                    if child is not None:
                        queue.append(child)
        except Exception:
            pass
        return None

    def _app_name(self, element) -> Optional[str]:
        """The app's name, or None when it can't be told: that app is skipped."""
        try:
            pid = element.get_process_id()
            if pid == os.getpid():
                return None
            app = element.get_application()
            name = (app.get_name() if app else "") or ""
        except Exception:
            return None
        names = [name]
        self._names = name.lower()
        try:
            with open(f"/proc/{pid}/comm", encoding="utf-8") as f:
                names.append(f.read().strip())
            names.append(os.path.basename(os.readlink(f"/proc/{pid}/exe")))
        except Exception:
            pass
        self._names = " ".join(n.lower() for n in names if n)
        return name or (names[1] if len(names) > 1 else None)

    def _is_skipped(self, element, app: str) -> bool:
        if any(skip in self._names for skip in self.SKIPPED_APPS):
            return True
        try:
            role = element.get_role()
            role_name = role.value_nick.upper().replace("-", "_")
            if role in (Atspi.Role.PASSWORD_TEXT, Atspi.Role.TERMINAL):
                return True
            if role_name not in self.TEXT_ROLES:
                return True
            states = element.get_state_set()
            if not states.contains(Atspi.StateType.EDITABLE):
                return True
            # Web pages mark password and search inputs with their input type.
            attrs = element.get_attributes() or {}
            if attrs.get("text-input-type", "").lower() in ("password", "search"):
                return True
            if attrs.get("xml-roles", "").lower() in ("searchbox", "search"):
                return True
        except Exception:
            return True
        return False

    def _text(self, element) -> Optional[str]:
        try:
            length = Atspi.Text.get_character_count(element)
            if length > self.MAX_LENGTH:
                return None
            text = Atspi.Text.get_text(element, 0, length) if length else ""
        except Exception:
            return None
        # A field that shows only dots or stars is a password field in disguise.
        if text and set(text.strip()) <= set("•●*·∙"):
            return None
        return text
