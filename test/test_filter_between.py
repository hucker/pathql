import os
import pathlib
import time

from pathql.filters import AgeHours, AgeMinutes, Between, Size
from pathql.filters.stat_proxy import StatProxy


def touch(path: pathlib.Path, mtime: float | None = None) -> None:
    """Create a file and optionally set its modification time."""
    path.touch()
    if mtime is not None:
        atime = mtime
        path.stat()  # ensure file exists
        os.utime(str(path), (atime, mtime))


def test_between_age_hours(tmp_path: pathlib.Path) -> None:
    """Between with AgeHours matches files in the provided hour range."""
    # Arrange
    test_path = tmp_path / "f.txt"
    now = time.time()
    mtime = now - 2.5 * 3600
    touch(test_path, mtime)

    # Act and Assert
    age_between = Between(AgeHours(), 2, 3)
    assert age_between.match(test_path, StatProxy(test_path)) is True
    age_below = Between(AgeHours(), 1, 2)
    assert age_below.match(test_path, StatProxy(test_path)) is False
    age_above = Between(AgeHours(), 3, 4)
    assert age_above.match(test_path, StatProxy(test_path)) is False


def test_between_age_minutes(tmp_path: pathlib.Path) -> None:
    """Between with AgeMinutes matches files in the provided minute range."""
    # Arrange
    test_path = tmp_path / "g.txt"
    now = time.time()
    mtime = now - 90 * 60
    touch(test_path, mtime)

    # Act and Assert
    min_between = Between(AgeMinutes(), 60, 120)
    assert min_between.match(test_path, StatProxy(test_path)) is True
    min_below = Between(AgeMinutes(), 0, 59)
    assert min_below.match(test_path, StatProxy(test_path)) is False
    min_above = Between(AgeMinutes(), 121, 180)
    assert min_above.match(test_path, StatProxy(test_path)) is False


def test_between_size(tmp_path: pathlib.Path) -> None:
    """Between with Size matches files between the provided byte bounds."""
    # Arrange
    test_path = tmp_path / "h.txt"
    test_path.write_bytes(b"x" * 1500)

    # Act and Assert
    size_between = Between(Size(), 1000, 2000)
    assert size_between.match(test_path, StatProxy(test_path)) is True
    size_below = Between(Size(), 0, 1000)
    assert size_below.match(test_path, StatProxy(test_path)) is False
    size_above = Between(Size(), 2001, 3000)
    assert size_above.match(test_path, StatProxy(test_path)) is False
    size_above = Between(Size(), 2001, 3000)
    assert size_above.match(test_path, StatProxy(test_path)) is False
