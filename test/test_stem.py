"""Tests for Stem and Name filters (equality, multiple, and wildcard)."""

import pathlib

import pytest

from pathql.filters.stem import Name, Stem


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_eq(cls: type) -> None:
    """Equality matching for Stem and Name filters."""
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls(["foo"]).match(f)
    assert not cls(["bar"]).match(f)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_multiple(cls: type) -> None:
    """Multiple stem matching works as expected."""
    # Arrange
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.txt")
    stem_filter = cls(["foo", "bar"])

    # Act and Assert
    assert stem_filter.match(f1)
    assert stem_filter.match(f2)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_string(cls: type) -> None:
    """String-based matching for Stem and Name filters."""
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls("foo").match(f)
    assert not cls("bar").match(f)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_wildcard(cls: type) -> None:
    """Wildcard matching for Stem and Name filters."""
    # Arrange
    f = pathlib.Path("foo123.txt")

    # Act and Assert
    assert cls("foo*").match(f)
    assert not cls("bar*").match(f)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_name_alias(cls: type) -> None:
    """Name alias behaves like Stem filter."""
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls("foo").match(f)
    assert not cls("bar").match(f)


@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_fnmatch_patterns(cls: type) -> None:
    """fnmatch patterns are supported for Stem/Name filters."""
    # Arrange
    f1 = pathlib.Path("foo123.txt")
    f2 = pathlib.Path("foo.txt")
    f3 = pathlib.Path("bar_foo.txt")
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
    assert cls("[a-z][a-z][a-z]", ignore_case=False).match(f8)
    assert not cls("[a-z][a-z][a-z]", ignore_case=False).match(f9)
