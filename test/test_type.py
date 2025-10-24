"""Tests for Type filter: file, directory, and symlink detection."""

import pathlib
import sys
from typing import cast

import pytest

from pathql.filters.file_type import FileType


def test_type_file(tmp_path: pathlib.Path) -> None:
    """Type.FILE matches a regular file."""
    # Arrange
    f = tmp_path / "a.txt"
    f.write_text("A")

    # Act and Assert
    assert FileType().file.match(f)


def test_type_directory(tmp_path: pathlib.Path) -> None:
    """Type.DIRECTORY matches a directory."""
    # Arrange
    d = tmp_path / "dir"
    d.mkdir()

    # Act and Assert
    assert (FileType().directory ).match(d)


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
    assert (FileType().link).match(link)
    assert not (FileType().file).match(link)




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
    assert FileType().unknown.match(cast(pathlib.Path, bad))
    assert not FileType().file.match(cast(pathlib.Path, bad))
    if sys.platform.startswith("win"):
        pytest.skip("Symlink tests are skipped on Windows.")

    broken = tmp_path / "broken_link"
    # Ensure we don't error if the link/file already exists (tests may be re-run)
    if broken.exists() or broken.is_symlink():
        broken.unlink(missing_ok=True)
    broken.symlink_to(tmp_path / "does_not_exist.txt")

    assert (FileType().link).match(broken)

    broken = tmp_path / "broken_link"
    if broken.exists() or broken.is_symlink():
        broken.unlink(missing_ok=True)
    broken.symlink_to(tmp_path / "does_not_exist.txt")
    assert (FileType().link).match(broken)
