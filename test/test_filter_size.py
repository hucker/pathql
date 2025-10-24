"""Tests for Size filter using fixture files with known sizes."""

# Tests for Size filter using the size_test_folder fixture.
# size_test_folder contains:
#   100.txt (100 bytes)
#   200.txt (200 bytes)

import pathlib

from pathql.filters.size import Size
from pathql.filters.stat_proxy import StatProxy


def test_size_eq(size_test_folder: pathlib.Path) -> None:
    """Equality operator matches expected files by size."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert any((Size() == 100).match(f, StatProxy(f)) for f in files)
    assert any((Size() == 200).match(f, StatProxy(f)) for f in files)
    assert not any((Size() == 150).match(f, StatProxy(f)) for f in files)


def test_size_ne(size_test_folder: pathlib.Path) -> None:
    """Inequality operator matches expected files by size."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() != 150).match(f, StatProxy(f)) for f in files)
    assert any((Size() != 100).match(f, StatProxy(f)) for f in files)


def test_size_lt(size_test_folder: pathlib.Path) -> None:
    """Less-than operator matches files below the threshold."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() < 300).match(f, StatProxy(f)) for f in files)
    assert any((Size() < 150).match(f, StatProxy(f)) for f in files)
    assert not any((Size() < 100).match(f, StatProxy(f)) for f in files)


def test_size_le(size_test_folder: pathlib.Path) -> None:
    """Less-than-or-equal operator matches files at or below threshold."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() <= 200).match(f, StatProxy(f)) for f in files)
    assert any((Size() <= 100).match(f, StatProxy(f)) for f in files)
    assert not any((Size() <= 50).match(f, StatProxy(f)) for f in files)


def test_size_gt(size_test_folder: pathlib.Path) -> None:
    """Greater-than operator matches files above the threshold."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert any((Size() > 100).match(f, StatProxy(f)) for f in files)
    assert not any((Size() > 200).match(f, StatProxy(f)) for f in files)


def test_size_ge(size_test_folder: pathlib.Path) -> None:
    """Greater-than-or-equal operator matches files at or above threshold."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() >= 100).match(f, StatProxy(f)) for f in files)
    assert any((Size() >= 200).match(f, StatProxy(f)) for f in files)
    assert not any((Size() >= 300).match(f, StatProxy(f)) for f in files)
    assert any((Size() >= 200).match(f, StatProxy(f)) for f in files)
    assert not any((Size() >= 300).match(f, StatProxy(f)) for f in files)
