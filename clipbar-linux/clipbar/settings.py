"""Settings and configuration management for ClipBar."""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def get_config_dir() -> Path:
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        base = Path(xdg_config)
    else:
        base = Path.home() / ".config"
    config_dir = base / "clipbar"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_dir() -> Path:
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        base = Path(xdg_data)
    else:
        base = Path.home() / ".local" / "share"
    data_dir = base / "clipbar"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


class Settings:
    """Manages ClipBar user preferences with atomic file persistence."""

    _instance: Optional[Settings] = None

    # Bounds matching Swift Settings.swift
    DRAFT_LENGTH_RANGE = (10, 500)
    DRAFT_HOUR_RANGE = (1, 168)
    DRAFT_COUNT_RANGE = (1, 50)
    KEEP_DAYS_RANGE = (1, 365)
    MAX_ITEMS_RANGE = (50, 2000)

    DEFAULT_VALUES: Dict[str, Any] = {
        "clearAfterDays": 30,
        "clearAfterCount": 500,
        "clearPinned": False,
        "autoPaste": True,
        "skipSensitive": True,
        "captureScreenshots": True,
        "copyScreenshots": True,
        "draftsEnabled": False,
        "draftMinLength": 30,
        "draftHours": 12,
        "draftCount": 10,
        "shortcut": "Ctrl+Shift+V",
    }

    @classmethod
    def shared(cls) -> Settings:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._path = get_config_dir() / "settings.json"
        self._listeners: List[Callable[[str, Any], None]] = []
        self._data: Dict[str, Any] = dict(self.DEFAULT_VALUES)
        self.load()

    def add_listener(self, callback: Callable[[str, Any], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str, Any], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, key: str, value: Any) -> None:
        for listener in list(self._listeners):
            try:
                listener(key, value)
            except Exception:
                pass

    def load(self) -> None:
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self._data.update(loaded)
            except Exception:
                pass

    def save(self) -> None:
        temp_path = self._path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            temp_path.replace(self._path)
        except Exception:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    # --- Properties ---

    @property
    def keep_days(self) -> int:
        return clamp(int(self._data.get("clearAfterDays", 30)), *self.KEEP_DAYS_RANGE)

    @keep_days.setter
    def keep_days(self, val: int) -> None:
        v = clamp(int(val), *self.KEEP_DAYS_RANGE)
        if self._data.get("clearAfterDays") != v:
            self._data["clearAfterDays"] = v
            self.save()
            self._notify("keepDays", v)

    @property
    def max_items(self) -> int:
        return clamp(int(self._data.get("clearAfterCount", 500)), *self.MAX_ITEMS_RANGE)

    @max_items.setter
    def max_items(self, val: int) -> None:
        v = clamp(int(val), *self.MAX_ITEMS_RANGE)
        if self._data.get("clearAfterCount") != v:
            self._data["clearAfterCount"] = v
            self.save()
            self._notify("maxItems", v)

    @property
    def clean_pinned(self) -> bool:
        return bool(self._data.get("clearPinned", False))

    @clean_pinned.setter
    def clean_pinned(self, val: bool) -> None:
        v = bool(val)
        if self._data.get("clearPinned") != v:
            self._data["clearPinned"] = v
            self.save()
            self._notify("cleanPinned", v)

    @property
    def auto_paste(self) -> bool:
        return bool(self._data.get("autoPaste", True))

    @auto_paste.setter
    def auto_paste(self, val: bool) -> None:
        v = bool(val)
        if self._data.get("autoPaste") != v:
            self._data["autoPaste"] = v
            self.save()
            self._notify("autoPaste", v)

    @property
    def skip_sensitive(self) -> bool:
        return bool(self._data.get("skipSensitive", True))

    @skip_sensitive.setter
    def skip_sensitive(self, val: bool) -> None:
        v = bool(val)
        if self._data.get("skipSensitive") != v:
            self._data["skipSensitive"] = v
            self.save()
            self._notify("skipSensitive", v)

    @property
    def capture_screenshots(self) -> bool:
        return bool(self._data.get("captureScreenshots", True))

    @capture_screenshots.setter
    def capture_screenshots(self, val: bool) -> None:
        v = bool(val)
        if self._data.get("captureScreenshots") != v:
            self._data["captureScreenshots"] = v
            self.save()
            self._notify("captureScreenshots", v)

    @property
    def copy_screenshots(self) -> bool:
        return bool(self._data.get("copyScreenshots", True))

    @copy_screenshots.setter
    def copy_screenshots(self, val: bool) -> None:
        v = bool(val)
        if self._data.get("copyScreenshots") != v:
            self._data["copyScreenshots"] = v
            self.save()
            self._notify("copyScreenshots", v)

    @property
    def drafts_enabled(self) -> bool:
        return bool(self._data.get("draftsEnabled", False))

    @drafts_enabled.setter
    def drafts_enabled(self, val: bool) -> None:
        v = bool(val)
        if self._data.get("draftsEnabled") != v:
            self._data["draftsEnabled"] = v
            self.save()
            self._notify("draftsEnabled", v)

    @property
    def draft_min_length(self) -> int:
        return clamp(int(self._data.get("draftMinLength", 30)), *self.DRAFT_LENGTH_RANGE)

    @draft_min_length.setter
    def draft_min_length(self, val: int) -> None:
        v = clamp(int(val), *self.DRAFT_LENGTH_RANGE)
        if self._data.get("draftMinLength") != v:
            self._data["draftMinLength"] = v
            self.save()
            self._notify("draftMinLength", v)

    @property
    def draft_hours(self) -> int:
        return clamp(int(self._data.get("draftHours", 12)), *self.DRAFT_HOUR_RANGE)

    @draft_hours.setter
    def draft_hours(self, val: int) -> None:
        v = clamp(int(val), *self.DRAFT_HOUR_RANGE)
        if self._data.get("draftHours") != v:
            self._data["draftHours"] = v
            self.save()
            self._notify("draftHours", v)

    @property
    def draft_count(self) -> int:
        return clamp(int(self._data.get("draftCount", 10)), *self.DRAFT_COUNT_RANGE)

    @draft_count.setter
    def draft_count(self, val: int) -> None:
        v = clamp(int(val), *self.DRAFT_COUNT_RANGE)
        if self._data.get("draftCount") != v:
            self._data["draftCount"] = v
            self.save()
            self._notify("draftCount", v)

    @property
    def shortcut(self) -> str:
        return str(self._data.get("shortcut", "Ctrl+Shift+V"))

    @shortcut.setter
    def shortcut(self, val: str) -> None:
        v = str(val).strip() or "Ctrl+Shift+V"
        if self._data.get("shortcut") != v:
            self._data["shortcut"] = v
            self.save()
            self._notify("shortcut", v)
