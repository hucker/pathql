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
from pathql.presets.dates import modified_this_minute,modified_this_hour
from pathql.presets.dates import modified_today, modified_this_month, modified_this_year

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
    # Arrange
    base = tmp_path_factory.mktemp("mod_presets")
    files: Dict[str, pathlib.Path] = {}
    for i, offset in enumerate(MOD_OFFSETS):
        f = base / f"file_{i}.txt"
        f.write_text(f"file_{i}")
        mtime = (BASE_TIME + offset).timestamp()
        os.utime(f, (mtime, mtime))
        files[f"file_{i}"] = f
    return files


import pytest

@pytest.mark.parametrize("preset_func", [
    modified_this_minute,
    modified_this_hour,
    modified_today,
    modified_this_month,
    modified_this_year,
])
def test_modified_presets_per_file(mod_files: Dict[str, pathlib.Path], preset_func: Callable):
    """
    For each file, use its mtime as 'now' and check which files match the preset.
    This robustly tests the preset logic for all possible 'now' values in the test set.
    """
    for label, f in mod_files.items():
        stat = f.stat()
        now = dt.datetime.fromtimestamp(stat.st_mtime)
        preset: Filter = preset_func(now)
        matched = [
            l for l, f2 in mod_files.items()
            if preset.match(f2, now=now, stat_result=f2.stat())
        ]
        # The file whose mtime matches 'now' should always be in the result
        assert label in matched, (
            f"{preset_func.__name__}: file {label} (mtime={now}) should match itself. "
            f"Matched: {matched}"
        )


