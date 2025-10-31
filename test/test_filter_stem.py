"""Tests for Stem  filters (equality, multiple, and wildcard)."""

import pathlib

import pytest

from pathql.filters.stem import Stem


@pytest.mark.parametrize("cls", [Stem])
def test_stem_eq(cls: type) -> None:
    """Equality matching for Stem  filters."""
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls(["foo"]).match(f)
    assert not cls(["bar"]).match(f)


@pytest.mark.parametrize("cls", [Stem ])
def test_stem_multiple(cls: type) -> None:
    """Multiple stem matching works as expected."""
    # Arrange
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.txt")
    stem_filter = cls(["foo", "bar"])

    # Act and Assert
    assert stem_filter.match(f1)
    assert stem_filter.match(f2)


@pytest.mark.parametrize("cls", [Stem ])
def test_stem_string(cls: type) -> None:
    """String-based matching for Stem  filters."""
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls("foo").match(f)
    assert not cls("bar").match(f)


@pytest.mark.parametrize("cls", [Stem ])
def test_stem_wildcard(cls: type) -> None:
    """Wildcard matching for Stem  filters."""
    # Arrange
    f = pathlib.Path("foo123.txt")

    # Act and Assert
    assert cls("foo*").match(f)
    assert not cls("bar*").match(f)


@pytest.mark.parametrize("cls", [Stem ])
def test_name_alias(cls: type) -> None:
    """Name alias behaves like Stem filter."""
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert cls("foo").match(f)
    assert not cls("bar").match(f)


@pytest.mark.parametrize("cls", [Stem ])
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


def test_stem_eq_new_style() -> None:
    """Test Stem() == ... matches file stems."""
    # Arrange
    f_foo = pathlib.Path("foo.txt")
    f_bar = pathlib.Path("bar.txt")
    # Act & Assert
    assert (Stem() == "foo").match(f_foo)
    assert not (Stem() == "foo").match(f_bar)
    assert (Stem() == ["foo", "bar"]).match(f_foo)
    assert (Stem() == ["foo", "bar"]).match(f_bar)

def test_stem_ne_new_style() -> None:
    """Test Stem() != ... negates file stem matching."""
    # Arrange
    f_foo = pathlib.Path("foo.txt")
    f_bar = pathlib.Path("bar.txt")
    # Act & Assert
    assert not (Stem() != "foo").match(f_foo)
    assert (Stem() != "foo").match(f_bar)

@pytest.mark.parametrize("op", [
    lambda s: s < "foo",
    lambda s: s <= "foo",
    lambda s: s > "foo",
    lambda s: s >= "foo",
    lambda s: s ^ "foo",
    lambda s: s % "foo",
    lambda s: s // "foo",
    lambda s: s + "foo",
    lambda s: s - "foo",
    lambda s: s * "foo",
    lambda s: s / "foo",
])
def test_stem_unsupported_operators(op) -> None:
    """Test Stem raises for unsupported operators."""
    # Arrange
    s = Stem()
    # Act & Assert
    with pytest.raises(NotImplementedError):
        op(s)

def test_stem_case_sensitivity() -> None:
    """Test Stem(ignore_case=...) matches stems with/without case sensitivity."""
    # Arrange
    f_upper = pathlib.Path("FOO.txt")
    f_lower = pathlib.Path("foo.txt")
    # Act & Assert
    # Case-insensitive (default)
    assert (Stem(ignore_case=True) == "foo").match(f_upper)
    assert (Stem(ignore_case=True) == "FOO").match(f_lower)
    # Case-sensitive
    assert (Stem(ignore_case=False) == "FOO").match(f_upper)
    assert not (Stem(ignore_case=False) == "FOO").match(f_lower)