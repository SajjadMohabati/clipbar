"""Main entry point for ClipBar Linux matching main.swift."""

from __future__ import annotations
import argparse
import os
import signal
import socket
import sys
import threading
from pathlib import Path


def get_socket_path() -> str:
    uid = os.getuid() if hasattr(os, "getuid") else 1000
    return f"/tmp/clipbar-{uid}.sock"


def send_to_existing_instance(command: str) -> bool:
    sock_path = get_socket_path()
    if not os.path.exists(sock_path):
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(sock_path)
        s.sendall(command.encode("utf-8"))
        s.close()
        return True
    except Exception:
        # Stale socket file
        try:
            os.unlink(sock_path)
        except Exception:
            pass
        return False


def start_ipc_server(app_controller) -> None:
    from clipbar.qt import QtCore, Signal

    class Bridge(QtCore.QObject):
        # Emitted on the listener thread, delivered on the GUI thread (queued connection).
        command = Signal(str)

    bridge = Bridge()
    actions = {
        "toggle": app_controller.toggle_panel,
        "settings": app_controller.open_settings,
        "quit": app_controller.quit,
    }
    bridge.command.connect(lambda name: actions.get(name, lambda: None)())
    app_controller._ipc_bridge = bridge  # keep it alive

    sock_path = get_socket_path()
    if os.path.exists(sock_path):
        try:
            os.unlink(sock_path)
        except Exception:
            pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(sock_path)
    os.chmod(sock_path, 0o600)
    server.listen(5)

    def loop():
        while True:
            try:
                conn, _ = server.accept()
            except OSError:
                break
            try:
                data = conn.recv(1024).decode("utf-8").strip()
            except Exception:
                data = ""
            finally:
                conn.close()
            if data in actions:
                bridge.command.emit(data)

    threading.Thread(target=loop, daemon=True).start()


def main() -> int:
    parser = argparse.ArgumentParser(description="ClipBar — Modern clipboard manager for Linux")
    parser.add_argument("--toggle", action="store_true", help="Toggle the ClipBar panel")
    parser.add_argument("--settings", action="store_true", help="Open ClipBar settings")
    parser.add_argument("--version", action="version", version="ClipBar 1.0 (Linux)")
    args = parser.parse_args()

    # Check if instance already running
    if args.toggle:
        if send_to_existing_instance("toggle"):
            return 0
    elif args.settings:
        if send_to_existing_instance("settings"):
            return 0
    else:
        # Plain launch: if already running, toggle panel and exit
        if send_to_existing_instance("toggle"):
            return 0

    # Initialize Qt
    from clipbar.qt import QApplication, QT_BINDING
    if QT_BINDING is None:
        print("Error: Neither PyQt6 nor PySide6 is installed.", file=sys.stderr)
        print("Please install PyQt6: sudo apt install python3-pyqt6 (Ubuntu/Debian) or pip install PyQt6", file=sys.stderr)
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("ClipBar")
    app.setApplicationDisplayName("ClipBar")
    app.setQuitOnLastWindowClosed(False)
    # Inter is the closest open font to Apple's SF Pro; Noto covers Persian, Arabic and emoji.
    from clipbar.qt import QFont
    font = QFont()
    font.setFamilies(["Inter", "Noto Sans", "Noto Sans Arabic", "Noto Color Emoji", "Sans Serif"])
    font.setPointSizeF(10)
    app.setFont(font)

    from clipbar.app import ClipBarApp
    controller = ClipBarApp(app)
    controller.launch()

    # Start single-instance IPC server
    start_ipc_server(controller)

    # Clean signal handling
    signal.signal(signal.SIGINT, lambda *_: controller.quit())
    signal.signal(signal.SIGTERM, lambda *_: controller.quit())

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
