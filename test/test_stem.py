"""
Tests for Stem and Name filters, including equality and multiple stem matching.
"""

import pathlib
import pytest
from pathql.filters.stem import Stem, Name


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_eq(cls: type) -> None:
    """
    Test equality matching for Stem and Name filters.

    - Arrange: Create a file path.
    - Act: Apply equality filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls(["foo"]).match(f)
    assert not cls(["bar"]).match(f)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_multiple(cls: type) -> None:
    """
    Test multiple stem matching for Stem and Name filters.

    - Arrange: Create multiple file paths.
    - Act: Apply multiple stem filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.txt")
    stem_filter = cls(["foo", "bar"])

    # Act and Assert
    assert stem_filter.match(f1)
    assert stem_filter.match(f2)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_string(cls: type) -> None:
    """
    Test string-based matching for Stem and Name filters.

    - Arrange: Create a file path.
    - Act: Apply string-based filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls("foo").match(f)
    assert not cls("bar").match(f)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_wildcard(cls: type) -> None:
    """
    Test wildcard matching for Stem and Name filters.

    - Arrange: Create a file path.
    - Act: Apply wildcard filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f = pathlib.Path("foo123.txt")

    # Act and Assert
    assert cls("foo*").match(f)
    assert not cls("bar*").match(f)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_name_alias(cls: type) -> None:
    """
    Test alias matching for Stem and Name filters.

    - Arrange: Create a file path.
    - Act: Apply alias filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls("foo").match(f)
    assert not cls("bar").match(f)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_fnmatch_patterns(cls: type) -> None:
    """
    Test fnmatch pattern matching for Stem and Name filters.

    - Arrange: Create file paths.
    - Act: Apply fnmatch pattern filters.
    - Assert: Verify matching results.
    """
    # Arrange
    f1 = pathlib.Path("foo123.txt")
    f2 = pathlib.Path("foo.txt")
    f3 = pathlib.Path("barfoo.txt")
    f4 = pathlib.Path("file1.txt")
    f5 = pathlib.Path("fileA.txt")
    f6 = pathlib.Path("bar.txt")
    f7 = pathlib.Path("foobar.txt")
    f8 = pathlib.Path("abc.txt")
    f9 = pathlib.Path("Abc.txt")

    # Act and Assert
    assert cls("foo*").match(f1)
    assert cls("foo*").match(f2)
    assert not cls("foo*").match(f3)
    assert cls("*1").match(f4)
    assert not cls("*1").match(f5)
    assert cls("bar").match(f6)
    assert not cls("bar").match(f7)
    assert cls("[a-z][a-z][a-z]", ignore_case=False).match(f8)
    assert not cls("[a-z][a-z][a-z]", ignore_case=False).match(f9)
