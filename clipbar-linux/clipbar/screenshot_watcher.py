"""Watches system screenshot directory matching ScreenshotWatcher.swift."""

from __future__ import annotations
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Set


class ScreenshotWatcher:
    """Detects new screenshots on Linux (GNOME/Ubuntu, KDE, XFCE)."""

    def __init__(self, on_screenshot: Callable[[Path], None]) -> None:
        self.on_screenshot = on_screenshot
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._seen: Set[str] = set()
        self._start_time: float = time.time()
        self._current_folder: Optional[Path] = None

    @classmethod
    def get_screenshot_folder(cls) -> Path:
        """Determines screenshot folder for GNOME, KDE, or generic XDG."""
        # 1. Check GNOME 42+ default: ~/Pictures/Screenshots
        home = Path.home()
        pictures_dir = home / "Pictures"

        # Check xdg-user-dir PICTURES
        try:
            res = subprocess.run(["xdg-user-dir", "PICTURES"], stdout=subprocess.PIPE, text=True, check=False)
            if res.returncode == 0 and res.stdout.strip():
                pictures_dir = Path(res.stdout.strip())
        except Exception:
            pass

        gnome_screenshots = pictures_dir / "Screenshots"
        if gnome_screenshots.exists():
            return gnome_screenshots

        # If Screenshots subfolder doesn't exist yet, but Pictures does
        if pictures_dir.exists():
            return pictures_dir

        return home

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._start_time = time.time()
        self._current_folder = self.get_screenshot_folder()

        # Seed initial existing files so we only detect new ones
        if self._current_folder.exists():
            try:
                for f in self._current_folder.iterdir():
                    if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                        self._seen.add(str(f.resolve()))
            except Exception:
                pass

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread = None

    def _run_loop(self) -> None:
        while self._running:
            time.sleep(1.5)
            # Re-check folder in case ~/Pictures/Screenshots was created
            latest_folder = self.get_screenshot_folder()
            if latest_folder != self._current_folder:
                self._current_folder = latest_folder

            if not self._current_folder or not self._current_folder.exists():
                continue

            try:
                for f in self._current_folder.iterdir():
                    if not self._running:
                        break
                    if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                        abs_p = str(f.resolve())
                        if abs_p not in self._seen:
                            self._seen.add(abs_p)
                            # Check file modification time to make sure it's newly created
                            try:
                                mtime = f.stat().st_mtime
                                if mtime >= self._start_time - 5:  # small grace window
                                    self.on_screenshot(f)
                            except Exception:
                                pass
            except Exception:
                pass
