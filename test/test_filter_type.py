"""Tests for Type filter: file, directory, and symlink detection."""

import pathlib
import sys

import pytest

from pathql.filters.file_type import FileType
from pathql.filters.stat_proxy import StatProxy


def test_type_file(tmp_path: pathlib.Path) -> None:
    """Type.FILE matches a regular file."""
    # Arrange
    f = tmp_path / "a.txt"
    f.write_text("A")

    # Act and Assert
    assert (FileType().file).match(f, StatProxy(f))


def test_type_directory(tmp_path: pathlib.Path) -> None:
    """Type.DIRECTORY matches a directory."""
    # Arrange
    d = tmp_path / "dir"
    d.mkdir()

    # Act and Assert
    assert (FileType().directory).match(d, StatProxy(d))


def test_type_link(tmp_path: pathlib.Path) -> None:
    """Type.LINK matches symlinks and not files or directories."""
    # Arrange
    if sys.platform.startswith("win"):
        pytest.skip("Symlink tests are skipped on Windows.")
    f = tmp_path / "foo.txt"
    f.write_text("hello")
    link = tmp_path / "foo_link.txt"
    link.symlink_to(f)

    # Act and Assert
    assert (FileType().link).match(link, StatProxy(link))
    assert not (FileType().file).match(link, StatProxy(link))


def test_type_no_type_name_raises(tmp_path):
    """Type filter with no type_name should not match anything and should not raise."""
    f = tmp_path / "foo.txt"
    f.write_text("x")
    t = FileType()
    # Should always return False for any file type
    assert not t.match(f, StatProxy(f))
    assert not t.match(tmp_path, StatProxy(tmp_path))


def test_type_invalid_type_name(tmp_path):
    """Type filter with an invalid type_name should never match and should not raise."""
    f = tmp_path / "foo.txt"
    f.write_text("x")
    t = FileType("not_a_type")
    # Should always return False for any file type
    assert not t.match(f, StatProxy(f))
    assert not t.match(tmp_path, StatProxy(tmp_path))


def test_type_unknown_on_missing_file(tmp_path):
    """Type().unknown should match missing files, others should not."""
    missing = tmp_path / "does_not_exist.txt"
    assert FileType().unknown.match(missing, StatProxy(missing))
    assert not FileType().file.match(missing, StatProxy(missing))
    assert not FileType().directory.match(missing, StatProxy(missing))
    assert not FileType().link.match(missing, StatProxy(missing))
