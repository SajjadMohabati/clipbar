"""Global shortcut handling matching HotKey.swift."""

from __future__ import annotations
import threading
from typing import Callable, Optional

# Try importing pynput or keybinder for system-wide shortcuts
_HOTKEY_BACKEND = None
try:
    from pynput import keyboard
    _HOTKEY_BACKEND = "pynput"
except ImportError:
    try:
        import gi
        gi.require_version('Keybinder', '3.0')
        from gi.repository import Keybinder
        Keybinder.init()
        _HOTKEY_BACKEND = "keybinder"
    except Exception:
        pass


class HotKey:
    """Manages system-wide global shortcut registration on Linux."""

    _instance: Optional[HotKey] = None

    @classmethod
    def shared(cls) -> HotKey:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._action: Callable[[], None] = lambda: None
        self._current_shortcut = "Ctrl+Shift+V"
        self._listener = None
        self._is_registered = False

    def install(self, action: Callable[[], None]) -> None:
        self._action = action

    def register(self, shortcut_str: str) -> None:
        self.unregister()
        self._current_shortcut = shortcut_str.strip() or "Ctrl+Shift+V"

        if _HOTKEY_BACKEND == "keybinder":
            try:
                # Convert Ctrl+Shift+V to <Ctrl><Shift>v for keybinder
                key_accel = self._to_keybinder_format(self._current_shortcut)
                Keybinder.bind(key_accel, lambda _: self._on_triggered())
                self._is_registered = True
                return
            except Exception:
                pass

        if _HOTKEY_BACKEND == "pynput":
            try:
                combo = self._to_pynput_format(self._current_shortcut)
                self._listener = keyboard.GlobalHotKeys({
                    combo: self._on_triggered
                })
                self._listener.start()
                self._is_registered = True
                return
            except Exception:
                pass

    def unregister(self) -> None:
        if not self._is_registered:
            return

        if _HOTKEY_BACKEND == "keybinder":
            try:
                key_accel = self._to_keybinder_format(self._current_shortcut)
                Keybinder.unbind(key_accel)
            except Exception:
                pass

        if _HOTKEY_BACKEND == "pynput" and self._listener:
            try:
                self._listener.stop()
                self._listener = None
            except Exception:
                pass

        self._is_registered = False

    def _on_triggered(self) -> None:
        # pynput calls this from its own listener thread.
        from clipbar.main_thread import run_on_main
        if self._action:
            run_on_main(self._action)

    @staticmethod
    def _to_keybinder_format(shortcut: str) -> str:
        parts = shortcut.split("+")
        accels = []
        key = ""
        for p in parts:
            p_lower = p.strip().lower()
            if p_lower in ("ctrl", "control"):
                accels.append("<Control>")
            elif p_lower in ("shift",):
                accels.append("<Shift>")
            elif p_lower in ("alt", "option"):
                accels.append("<Alt>")
            elif p_lower in ("super", "win", "meta", "command", "cmd"):
                accels.append("<Super>")
            else:
                key = p.strip().lower()
        return "".join(accels) + key

    @staticmethod
    def _to_pynput_format(shortcut: str) -> str:
        parts = shortcut.split("+")
        accels = []
        for p in parts:
            p_lower = p.strip().lower()
            if p_lower in ("ctrl", "control"):
                accels.append("<ctrl>")
            elif p_lower in ("shift",):
                accels.append("<shift>")
            elif p_lower in ("alt", "option"):
                accels.append("<alt>")
            elif p_lower in ("super", "win", "meta", "command", "cmd"):
                accels.append("<cmd>")
            else:
                accels.append(p.strip().lower())
        return "+".join(accels)
