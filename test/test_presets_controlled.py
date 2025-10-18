"""
Test PathQL date-based presets with strictly controlled modification times.
Creation time tests use mtime as a proxy (documented in test).
"""
from collections.abc import Callable
import os
from typing import Dict
import pathlib
import datetime as dt
import pytest
from pathql.presets.dates import  modified_this_minute,modified_this_hour, modified_today, modified_this_month, modified_this_year

from pathql.filters.base import Filter

BASE_TIME = dt.datetime(2025, 1, 1, 0, 0, 0)

MOD_OFFSETS = [
    dt.timedelta(),                # file_0: 2025-01-01 00:00:00
    dt.timedelta(minutes=1),       # file_1: +1 minute
    dt.timedelta(hours=1),         # file_2: +1 hour
    dt.timedelta(days=1),          # file_3: +1 day
    dt.timedelta(days=31),         # file_4: +1 month (approx)
    dt.timedelta(days=366),        # file_5: +1 year (approx)
]

@pytest.fixture(scope="module")
def mod_files(tmp_path_factory: pytest.TempPathFactory) -> Dict[str, pathlib.Path]:
    """
    Create files with strictly controlled modification times.
    Returns dict: {label: pathlib.Path}
    """
    base = tmp_path_factory.mktemp("mod_presets")
    files: Dict[str, pathlib.Path] = {}
    for i, offset in enumerate(MOD_OFFSETS):
        f = base / f"file_{i}.txt"
        f.write_text(f"file_{i}")
        mtime = (BASE_TIME + offset).timestamp()
        os.utime(f, (mtime, mtime))
        files[f"file_{i}"] = f
    return files

@pytest.mark.parametrize("preset_func, expected", [
    (modified_this_minute, ["file_0"]),
    (modified_this_hour, ["file_0", "file_1"]),
    (modified_today, ["file_0", "file_1", "file_2"]),
    (modified_this_month, ["file_0", "file_1", "file_2", "file_3"]),
    (modified_this_year, ["file_0", "file_1", "file_2", "file_3", "file_4"]),
])
def test_modified_presets_all(mod_files: Dict[str, pathlib.Path], preset_func: Callable, expected: list[str]):
    now = BASE_TIME
    preset: Filter = preset_func(now)
    matched = [label for label, f in mod_files.items() if preset.match(f, now=now.timestamp(), stat_result=f.stat())]
    assert set(matched) == set(expected), f"{preset_func.__name__}: expected {expected}, got {matched}"


