"""Runs work on the GUI thread. Qt widgets, the clipboard and the store's lists belong to it,
so background threads hand their results over here instead of touching them directly."""

from __future__ import annotations
import threading
from typing import Callable, Optional

_invoker = None


def install() -> None:
    """Call once on the GUI thread, after QApplication exists."""
    global _invoker
    from clipbar.qt import QtCore, Signal

    class _Invoker(QtCore.QObject):
        call = Signal(object)

        def __init__(self) -> None:
            super().__init__()
            # The receiver lives on the GUI thread, so emits from other threads are queued.
            self.call.connect(self._run)

        def _run(self, fn: Callable[[], None]) -> None:
            try:
                fn()
            except Exception:
                pass

    _invoker = _Invoker()


def run_on_main(fn: Callable[[], None]) -> None:
    """Runs `fn` now if this is the GUI thread, otherwise queues it there."""
    if threading.current_thread() is threading.main_thread() or _invoker is None:
        fn()
    else:
        _invoker.call.emit(fn)
