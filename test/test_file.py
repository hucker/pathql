"""Tests for File filter, especially curly-brace extension patterns and case insensitivity."""

import pytest
import pathlib
from pathql.filters import File

@pytest.mark.parametrize(
    "filename, pattern, should_match",
    [
        ("foo.jpg", "foo.{jpg,png,bmp}", True),
        ("foo.png", "foo.{jpg,png,bmp}", True),
        ("foo.bmp", "foo.{jpg,png,bmp}", True),
        ("foo.gif", "foo.{jpg,png,bmp}", False),
        ("bar.jpg", "foo.{jpg,png,bmp}", False),
        ("foo.JPG", "foo.{jpg,png,bmp}", True),  # case-insensitive
        ("foo.PnG", "foo.{jpg,png,bmp}", True),  # case-insensitive
        ("foo", "foo.{jpg,png,bmp}", False),     # no extension
        ("foo.jpg.txt", "foo.{jpg,png,bmp}", False), # wrong extension
    ]
)
def test_file_curly_brace_suffix(tmp_path: pathlib.Path, filename: str, pattern: str, should_match: bool) -> None:
    """
    Test File filter with curly-brace extension patterns.

    - Arrange: Create a file with the given filename.
    - Act: Apply the File filter with the specified pattern.
    - Assert: Verify that the filter matches the file correctly.
    """
    # Arrange
    f = make_file(tmp_path, filename)

    # Act and Assert
    assert File(pattern).match(f) is should_match


def make_file(tmp_path: pathlib.Path, name: str) -> pathlib.Path:
    """
    Create a file with the given name in the temporary directory.

    Args:
        tmp_path (pathlib.Path): Temporary directory provided by pytest.
        name (str): Name of the file to create.

    Returns:
        pathlib.Path: Path to the created file.
    """
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
        # Path object as pattern
        ("foo.db", pathlib.Path("foo.db"), True),
        ("foo.db", pathlib.Path("other.db"), False),
    ]
)
def test_file_patterns(tmp_path: pathlib.Path, filename: str, pattern: str, should_match: bool) -> None:
    """
    Test File filter with various patterns.

    - Arrange: Create a file with the given filename.
    - Act: Apply the File filter with the specified pattern.
    - Assert: Verify that the filter matches the file correctly.
    """
    # Arrange
    f = make_file(tmp_path, filename)

    # Act and Assert
    assert File(pattern).match(f) is should_match


def test_file_as_stem_and_suffix(tmp_path: pathlib.Path) -> None:
    """
    Test File filter's as_stem_and_suffix method.

    - Arrange: Create a file with a specific name.
    - Act: Apply the as_stem_and_suffix method.
    - Assert: Verify that the method returns the correct stem and suffix matchers.
    """
    # Arrange
    f = make_file(tmp_path, "foo.db")
    file_filter = File("foo.db")

    # Act
    result = file_filter.as_stem_and_suffix()

    # Assert
    assert result is not None
    if len(result) == 2:
        stem, suffix = result
        assert stem.match(f)
        assert suffix.match(f)
    else:
        pytest.fail("Expected a tuple of length 2 for stem and suffix")
    # Not for wildcards
    assert File("*.db").as_stem_and_suffix() is None
