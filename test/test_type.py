"""Tests for Type filter: file, directory, and symlink detection."""
import pathlib
from typing import cast
import sys
import pytest
from pathql.filters.type import Type

def test_type_file(tmp_path: pathlib.Path) -> None:
    """Type.FILE matches a regular file."""
    # Arrange
    f = tmp_path / "a.txt"
    f.write_text("A")

    # Act and Assert
    assert (Type == Type.FILE).match(f)

def test_type_directory(tmp_path: pathlib.Path) -> None:
    """Type.DIRECTORY matches a directory."""
    # Arrange
    d = tmp_path / "dir"
    d.mkdir()

    # Act and Assert
    assert (Type == Type.DIRECTORY).match(d)

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
    assert (Type == Type.LINK).match(link)
    assert not (Type == Type.FILE).match(link)

def test_type_union_and_set(tmp_path: pathlib.Path) -> None:
    """Type filter supports unions and set/string construction."""
    # Arrange
    f = tmp_path / "a.txt"
    f.write_text("A")
    d = tmp_path / "a_dir"
    d.mkdir()

    # Act and Assert
    type_union = {Type.FILE, Type.DIRECTORY}
    assert (Type == type_union).match(f)
    assert (Type == type_union).match(d)
    assert Type("file").match(f)
    assert Type("directory").match(d)
    assert Type({"file", "directory"}).match(f)
    assert Type({"file", "directory"}).match(d)

def test_type_contains() -> None:
    """Type filter supports membership testing via `in`."""
    # Arrange
    t = Type({Type.FILE, Type.DIRECTORY})

    # Act and Assert
    assert Type.FILE in t
    assert Type.DIRECTORY in t
    assert Type.LINK not in t

def test_type_or_and_ror() -> None:
    """OR operations produce a union of types."""
    # Arrange
    t1 = Type(Type.FILE)
    t2 = Type(Type.DIRECTORY)

    # Act
    t3 = t1 | t2
    t4 = t2.__ror__(t1)

    # Assert
    assert Type.FILE in t3.type_names and Type.DIRECTORY in t3.type_names
    assert t3.type_names == t4.type_names

def test_type_error_handling(
    tmp_path: pathlib.Path,
) -> None:
    """Type filter handles errors and recognizes UNKNOWN types."""
    # Arrange
    f = tmp_path / "err.txt"
    f.write_text("E")
    class BadPath:
        """A minimal Path-like stub that raises on lstat()."""

        def __init__(self, p: pathlib.Path) -> None:
            """Initialize with a Path."""
            self._p = p

        def exists(self) -> bool:
            """Always exists"""
            return True

        def lstat(self):
            """stat generates an OS Error."""
            raise OSError("fail")

    bad = BadPath(f)

    # Act and Assert
    # Cast to satisfy type checkers; BadPath implements only minimal Path-like API
    assert Type(Type.UNKNOWN).match(cast(pathlib.Path, bad))
    assert not Type(Type.FILE).match(cast(pathlib.Path, bad))
    if sys.platform.startswith("win"):
        pytest.skip("Symlink tests are skipped on Windows.")
    broken = tmp_path / "broken_link"
    broken.symlink_to(tmp_path / "does_not_exist.txt")
    assert (Type == Type.LINK).match(broken)
