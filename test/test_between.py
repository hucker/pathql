
import os
import time
import pytest
import pathlib
from pathql.filters import Between, AgeHours, AgeMinutes, Size

def touch(path, mtime: float | None = None) -> None:
    """Create a file and optionally set its mtime."""
    path.touch()
    if mtime is not None:
        atime = mtime
        path.stat()  # ensure file exists
        os.utime(path, (atime, mtime))



def test_between_age_hours(tmp_path: pathlib.Path) -> None:
    """Test Between filter for AgeHours."""
    test_path = tmp_path / "f.txt"
    now = time.time()
    mtime = now - 2.5 * 3600
    touch(test_path, mtime)
    age_between = Between(AgeHours(), 2, 3)
    assert age_between.match(test_path) is True
    age_below = Between(AgeHours(), 1, 2)
    assert age_below.match(test_path) is False
    age_above = Between(AgeHours(), 3, 4)
    assert age_above.match(test_path) is False

def test_between_age_minutes(tmp_path: pathlib.Path) -> None:
    """Test Between filter for AgeMinutes."""
    test_path = tmp_path / "g.txt"
    now = time.time()
    mtime = now - 90 * 60
    touch(test_path, mtime)
    min_between = Between(AgeMinutes(), 60, 120)
    assert min_between.match(test_path) is True
    min_below = Between(AgeMinutes(), 0, 59)
    assert min_below.match(test_path) is False
    min_above = Between(AgeMinutes(), 121, 180)
    assert min_above.match(test_path) is False

def test_between_size(tmp_path: pathlib.Path) -> None:
    """Test Between filter for Size with a 1500 byte file."""
    test_path = tmp_path / "h.txt"
    test_path.write_bytes(b"x" * 1500)
    size_between = Between(Size(), 1000, 2000)
    assert size_between.match(test_path) is True
    size_below = Between(Size(), 0, 1000)
    assert size_below.match(test_path) is False
    size_above = Between(Size(), 2001, 3000)
    assert size_above.match(test_path) is False
