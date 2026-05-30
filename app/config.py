"""Load config.json and resolve code vs data directory paths."""

from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import dataclass
from typing import Any


def install_root() -> str:
    """Folder containing config.json and the data directory (or the .exe when frozen)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@dataclass(frozen=True)
class AppPaths:
    install_root: str
    config_file: str
    data_dir: str
    bugs_file: str
    screenshots_dir: str
    reports_dir: str


@dataclass(frozen=True)
class WindowConfig:
    title: str
    width: int
    height: int
    min_width: int
    min_height: int


@dataclass(frozen=True)
class AppConfig:
    paths: AppPaths
    window: WindowConfig


def _read_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _ensure_config_file(root: str) -> str:
    config_path = os.path.join(root, "config.json")
    default_path = os.path.join(root, "config.default.json")
    if not os.path.exists(config_path):
        if os.path.exists(default_path):
            shutil.copy2(default_path, config_path)
        else:
            raise FileNotFoundError(
                f"Missing config.json and config.default.json in {root}"
            )
    return config_path


def _resolve_dir(root: str, path_value: str) -> str:
    if os.path.isabs(path_value):
        return path_value
    return os.path.join(root, path_value)


def _migrate_legacy_data(root: str, bugs_file: str, screenshots_dir: str) -> None:
    legacy_bugs = os.path.join(root, "bugs.json")
    if not os.path.exists(bugs_file) and os.path.exists(legacy_bugs):
        shutil.copy2(legacy_bugs, bugs_file)

    legacy_screenshots = os.path.join(root, "screenshots")
    if os.path.isdir(legacy_screenshots):
        for name in os.listdir(legacy_screenshots):
            src = os.path.join(legacy_screenshots, name)
            dst = os.path.join(screenshots_dir, name)
            if os.path.isfile(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)


def load_config() -> AppConfig:
    root = install_root()
    config_path = _ensure_config_file(root)
    raw = _read_json(config_path)

    data_dir = _resolve_dir(root, raw.get("data_directory", "data"))
    os.makedirs(data_dir, exist_ok=True)

    screenshots_dir = os.path.join(
        data_dir, raw.get("screenshots_subdirectory", "screenshots")
    )
    reports_dir = os.path.join(data_dir, raw.get("reports_subdirectory", "reports"))
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    bugs_file = os.path.join(data_dir, raw.get("bugs_filename", "bugs.json"))
    _migrate_legacy_data(root, bugs_file, screenshots_dir)

    paths = AppPaths(
        install_root=root,
        config_file=config_path,
        data_dir=data_dir,
        bugs_file=bugs_file,
        screenshots_dir=screenshots_dir,
        reports_dir=reports_dir,
    )

    win = raw.get("window", {})
    window = WindowConfig(
        title=win.get("title", "Bug Tracker - Panel QA"),
        width=int(win.get("width", 1000)),
        height=int(win.get("height", 700)),
        min_width=int(win.get("min_width", 800)),
        min_height=int(win.get("min_height", 600)),
    )

    return AppConfig(paths=paths, window=window)
