"""Tests for File filter: curly-brace extension patterns and case-insensitivity."""

import pathlib

import pytest

from pathql.filters import File


@pytest.mark.parametrize(
    "filename, pattern, should_match",
    [
        # Curly-brace expansion is NOT supported; these should all be False
        ("foo.jpg", "foo.{jpg,png,bmp}", False),
        ("foo.png", "foo.{jpg,png,bmp}", False),
        ("foo.bmp", "foo.{jpg,png,bmp}", False),
        ("foo.gif", "foo.{jpg,png,bmp}", False),
        ("bar.jpg", "foo.{jpg,png,bmp}", False),
        ("foo.JPG", "foo.{jpg,png,bmp}", False),
        ("foo.PnG", "foo.{jpg,png,bmp}", False),
        ("foo", "foo.{jpg,png,bmp}", False),
        ("foo.jpg.txt", "foo.{jpg,png,bmp}", False),
    ],
)
def test_file_curly_brace_suffix(
    tmp_path: pathlib.Path,
    filename: str,
    pattern: str,
    should_match: bool,
) -> None:
    """Curly-brace patterns are not supported by File filter."""
    # Arrange
    f = make_file(tmp_path, filename)

    # Act and Assert
    assert File(str(pattern)).match(f) is should_match


def make_file(tmp_path: pathlib.Path, name: str) -> pathlib.Path:
    """Create a file with the given name in the temporary directory."""
    file = tmp_path / name
    file.write_text("x")
    return file


@pytest.mark.parametrize(
    "filename, pattern, should_match",
    [
        # Exact match, case-insensitive
        ("Thumbs.db", "Thumbs.db", True),
        ("Thumbs.db", "thumbs.db", True),
        ("Thumbs.db", "other.db", False),
        # Wildcard extension
        ("foo.db", "*.db", True),
        ("foo.db", "*.txt", False),
        ("foo.txt", "*.db", False),
        ("foo.db", "foo.*", True),
        ("foo.db", "bar.*", False),
        ("foo.bmp", "*.bmp", True),
        ("bar.bmp", "*.bmp", True),
        ("foo.bmp", "foo.*", True),
        ("foo.bmp", "bar.*", False),
        # Wildcard stem
        ("foo123.db", "foo*", True),
        ("bar123.db", "foo*", False),
        ("foo123.db", "*123.db", True),
        ("foo123.db", "*23.db", True),
        ("foo123.db", "*99.db", False),
        # Path object as pattern (converted to str)
        ("foo.db", str(pathlib.Path("foo.db")), True),
        ("foo.db", str(pathlib.Path("other.db")), False),
    ],
)
def test_file_patterns(
    tmp_path: pathlib.Path,
    filename: str,
    pattern: str,
    should_match: bool,
) -> None:
    """File filter matches wildcard and exact patterns (case-insensitive)."""
    # Arrange
    f = make_file(tmp_path, filename)

    # Act and Assert
    assert File(str(pattern)).match(f) is should_match


## as_stem_and_suffix is no longer supported in File filter


## as_stem_and_suffix is no longer supported in File filter
