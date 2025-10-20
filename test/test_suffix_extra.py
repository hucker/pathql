"""Extra tests for Suffix and Ext filters, including nosplit and case-insensitive matching."""

import pytest
import pathlib
from pathql.filters.suffix import Suffix, Ext

def make_file(tmp_path: pathlib.Path, name: str) -> pathlib.Path:
    """
    Helper function to create a file with the given name.
    """
    file = tmp_path / name
    file.write_text("x")
    return file

def test_suffix_basic(tmp_path: pathlib.Path) -> None:
    """
    Test basic matching for Suffix and Ext filters.

    - Arrange: Create a file with a specific extension.
    - Act: Apply various suffix filters.
    - Assert: Verify matching results.
    """
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
    """
    Test no-split matching for Suffix filter.

    - Arrange: Create a file with a compound extension.
    - Act: Apply no-split filter.
    - Assert: Verify matching results.
    """
    # Arrange
    file = make_file(tmp_path, "foo.bar baz")

    # Act and Assert
    assert Suffix("bar baz", nosplit=True).match(file)
    assert not Suffix("bar baz").match(file)

def test_suffix_empty_patterns(tmp_path: pathlib.Path) -> None:
    """
    Test empty pattern handling for Suffix filter.

    - Arrange: Create a file with an extension.
    - Act: Apply an empty suffix filter.
    - Assert: Verify ValueError is raised.
    """
    # Arrange
    file = make_file(tmp_path, "foo.txt")

    # Act and Assert
    with pytest.raises(ValueError):
        Suffix().match(file)

def test_suffix_operator_overloads(tmp_path: pathlib.Path) -> None:
    """
    Test operator overloads for Suffix filter.

    - Arrange: Create a file with a specific extension.
    - Act: Apply various operator overloads.
    - Assert: Verify operator behavior.
    """
    # Arrange
    file = make_file(tmp_path, "foo.txt")

    # Act and Assert
    assert Suffix(["txt"]) == Suffix(["txt"])
    # Membership checks normalized dot-prefixed patterns
    assert ".txt" in Suffix(["txt", "md"])
    assert ".md" in Suffix(["txt", "md"])
    # Suffix("txt") returns a filter; test match directly
    assert Suffix("txt").match(file)
    # Suffix(["txt"]) returns a filter; test match directly
    assert Suffix(["txt"]).match(file)
    # Suffix(["txt", "md"]) returns a filter; test match directly
    assert Suffix(["txt", "md"]).match(file)
