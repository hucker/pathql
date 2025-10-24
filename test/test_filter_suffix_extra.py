"""Extra tests for Suffix and Ext filters, including nosplit and case-insensitive matching."""

import pathlib

import pytest

from pathql.filters.suffix import Ext, Suffix


def make_file(tmp_path: pathlib.Path, name: str) -> pathlib.Path:
    """Create a file with the given name inside tmp_path."""
    file = tmp_path / name
    file.write_text("x")
    return file


def test_suffix_basic(tmp_path: pathlib.Path) -> None:
    """Basic matching for Suffix and Ext filters."""
    # Arrange
    file = make_file(tmp_path, "foo.txt")

    # Act and Assert
    assert Suffix(".txt").match(file)
    assert not Suffix(".md").match(file)
    assert Suffix([".txt", ".md"]).match(file)
    assert Suffix(".txt .md").match(file)
    assert Suffix([".TXT"]).match(file)  # case-insensitive
    assert Ext(".txt").match(file)  # alias works
    # Permissive: '.txt' matches any file ending in .txt, even with multiple dots
    file2 = make_file(tmp_path, "foo.bar.txt")
    assert Suffix(".txt").match(file2)
    assert Ext(".txt").match(file2)


def test_suffix_nosplit(tmp_path: pathlib.Path) -> None:
    """No-split matching works for space-containing suffixes."""
    # Arrange
    file = make_file(tmp_path, "foo.bar baz")

    # Act and Assert
    assert Suffix("bar baz", nosplit=True).match(file)
    assert not Suffix("bar baz").match(file)


def test_suffix_empty_patterns(tmp_path: pathlib.Path) -> None:
    """Empty suffix patterns raise ValueError."""
    # Arrange
    file = make_file(tmp_path, "foo.txt")

    # Act and Assert
    with pytest.raises(ValueError):
        Suffix().match(file)


def test_suffix_operator_overloads(tmp_path: pathlib.Path) -> None:
    """Operator overloads behave as expected for Suffix."""
    # Arrange
    file = make_file(tmp_path, "foo.txt")

    # Act and Assert
    assert Suffix(["txt"]) == Suffix(["txt"])

    # Suffix("txt") returns a filter; test match directly
    assert Suffix("txt").match(file)
    # Suffix(["txt"]) returns a filter; test match directly
    assert Suffix(["txt"]).match(file)
    # Suffix(["txt", "md"]) returns a filter; test match directly
    assert Suffix(["txt", "md"]).match(file)
    assert Suffix(["txt"]).match(file)
    # Suffix(["txt", "md"]) returns a filter; test match directly
    assert Suffix(["txt", "md"]).match(file)
