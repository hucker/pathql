"""Operator tests for Size filter: ==, !=, <, >, <=, >=."""

import pathlib

from pathql.filters.size import Size
from pathql.filters.stat_proxy import StatProxy


def get_stat_proxy(path):
    return StatProxy(path)


def test_size_eq(size_test_folder: pathlib.Path) -> None:
    """Equality operator matches expected files by size."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert any((Size() == 100).match(f, get_stat_proxy(f)) for f in files)
    assert any((Size() == 200).match(f, get_stat_proxy(f)) for f in files)
    assert not any((Size() == 150).match(f, get_stat_proxy(f)) for f in files)


def test_size_ne(size_test_folder: pathlib.Path) -> None:
    """Inequality operator matches expected files by size."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() != 150).match(f, get_stat_proxy(f)) for f in files)
    assert any((Size() != 100).match(f, get_stat_proxy(f)) for f in files)


def test_size_lt(size_test_folder: pathlib.Path) -> None:
    """Less-than operator matches files below the threshold."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() < 300).match(f, get_stat_proxy(f)) for f in files)
    assert any((Size() < 150).match(f, get_stat_proxy(f)) for f in files)
    assert not any((Size() < 100).match(f, get_stat_proxy(f)) for f in files)


def test_size_le(size_test_folder: pathlib.Path) -> None:
    """Less-than-or-equal operator matches files at or below threshold."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() <= 200).match(f, get_stat_proxy(f)) for f in files)
    assert any((Size() <= 100).match(f, get_stat_proxy(f)) for f in files)
    assert not any((Size() <= 50).match(f, get_stat_proxy(f)) for f in files)


def test_size_gt(size_test_folder: pathlib.Path) -> None:
    """Greater-than operator matches files above the threshold."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert any((Size() > 100).match(f, get_stat_proxy(f)) for f in files)
    assert not any((Size() > 200).match(f, get_stat_proxy(f)) for f in files)


def test_size_ge(size_test_folder: pathlib.Path) -> None:
    """Greater-than-or-equal operator matches files at or above threshold."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() >= 100).match(f, get_stat_proxy(f)) for f in files)
    assert any((Size() >= 200).match(f, get_stat_proxy(f)) for f in files)
    assert not any((Size() >= 300).match(f, get_stat_proxy(f)) for f in files)
    assert any((Size() >= 200).match(f, get_stat_proxy(f)) for f in files)
    assert not any((Size() >= 300).match(f, get_stat_proxy(f)) for f in files)
