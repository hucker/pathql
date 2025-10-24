"""Tests for Suffix and Ext filters (operator, multi-extension, case-insensitive)."""

import pathlib
from typing import Type

import pytest

from pathql.filters.base import Filter
from pathql.filters.stat_proxy import StatProxy
from pathql.filters.suffix import Ext, Suffix


@pytest.mark.parametrize("suffix_class", [Suffix, Ext])
def test_suffix_eq(suffix_class: Type[Filter]) -> None:
    """Equality matching for Suffix/Ext filters."""
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert suffix_class("txt").match(f, StatProxy(f))
    assert not suffix_class("md").match(f, StatProxy(f))


@pytest.mark.parametrize("suffix_class", [Suffix, Ext])
def test_suffix_multiple(suffix_class: Type[Filter]) -> None:
    """Multiple extension matching works for Suffix/Ext."""
    # Arrange
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.md")
    suffix_filter = suffix_class(["txt", "md"])

    # Act and Assert
    assert suffix_filter.match(f1, StatProxy(f1))
    assert suffix_filter.match(f2, StatProxy(f2))


@pytest.mark.parametrize("suffix_class", [Suffix, Ext])
def test_suffix_case_insensitive(suffix_class: Type[Filter]) -> None:
    """Suffix and Ext are case-insensitive by default."""
    # Arrange
    f = pathlib.Path("foo.TXT")

    # Act and Assert
    assert suffix_class("txt").match(f, StatProxy(f))
    assert suffix_class("TXT").match(f, StatProxy(f))


@pytest.mark.parametrize("suffix_class", [Suffix, Ext])
def test_suffix_no_extension(suffix_class: Type[Filter]) -> None:
    """No extension file does not match suffix filters."""
    # Arrange
    f = pathlib.Path("foo")

    # Act and Assert
    assert not suffix_class("txt").match(f, StatProxy(f))


@pytest.mark.parametrize("suffix_class", [Suffix, Ext])
def test_suffix_whitespace_split(suffix_class: Type[Filter]) -> None:
    """Whitespace-separated patterns match multiple extensions."""
    # Arrange
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.bmp")
    suffix_filter = suffix_class("txt bmp")

    # Act and Assert
    assert suffix_filter.match(f1, StatProxy(f1))
    assert suffix_filter.match(f2, StatProxy(f2))
    assert not suffix_filter.match(
        pathlib.Path("baz.md"), StatProxy(pathlib.Path("baz.md"))
    )


@pytest.mark.parametrize("suffix_class", [Suffix, Ext])
def test_suffix_nosplit(suffix_class: Type[Filter]) -> None:
    """Nosplit matches exact multi-word suffixes only when nosplit=True."""
    # Arrange
    f = pathlib.Path("foo.txt bmp")
    suffix_filter = suffix_class("txt bmp", nosplit=True)
    suffix_filter2 = suffix_class("txt bmp")

    # Act and Assert
    assert suffix_filter.match(f, StatProxy(f))
    assert not suffix_filter2.match(f, StatProxy(f))


@pytest.mark.parametrize("suffix_class", [Suffix, Ext])
def test_suffix_dot_prefix_equivalence(suffix_class: Type[Suffix | Ext]) -> None:
    """Dot-prefixed and non-prefixed extensions are equivalent."""
    # Arrange
    f = pathlib.Path("image.jpg")
    f_upper = pathlib.Path("image.JPG")

    # Act & Assert
    assert suffix_class("jpg").match(f, StatProxy(f))
    assert suffix_class("jpg").match(f, StatProxy(f))
    assert suffix_class(".jpg").match(f, StatProxy(f))
    assert suffix_class(["jpg"]).match(f, StatProxy(f))
    assert suffix_class([".jpg"]).match(f, StatProxy(f))
    assert suffix_class("jpg").match(f_upper, StatProxy(f_upper))
    assert suffix_class(".jpg").match(f_upper, StatProxy(f_upper))
    assert suffix_class([".jpg", "txt"]).match(f, StatProxy(f))
    assert suffix_class(["jpg", ".txt"]).match(f, StatProxy(f))
    assert suffix_class("{.jpg,.png}").match(f, StatProxy(f))
    assert suffix_class("{jpg,png}").match(f, StatProxy(f))
    assert not suffix_class("png").match(f, StatProxy(f))
    assert not suffix_class([".png"]).match(f, StatProxy(f))
    assert not suffix_class("png").match(f, StatProxy(f))
    assert not suffix_class([".png"]).match(f, StatProxy(f))


@pytest.mark.parametrize("suffix_class", [Suffix, Ext])
def test_suffix_multi_part_extensions(suffix_class) -> None:
    """Multi-part extension matching behaves as expected for Suffix/Ext."""
    # Arrange
    f1 = pathlib.Path("archive.tar.gz")
    f2 = pathlib.Path("image.tif.back")
    f3 = pathlib.Path("foo.txt.back")
    f4 = pathlib.Path("foo.back")
    f5 = pathlib.Path("foo.tif")
    f6 = pathlib.Path("foo.tar.zip")

    # Act & Assert
    assert suffix_class(".tar.gz").match(f1, StatProxy(f1))
    assert not suffix_class(".tar.gz").match(f2, StatProxy(f2))
    assert suffix_class(".tar.gz").match(
        pathlib.Path("foo.bar.tar.gz"), StatProxy(pathlib.Path("foo.bar.tar.gz"))
    )
    assert suffix_class(".tif.back").match(f2, StatProxy(f2))
    assert suffix_class(".tif.back").match(
        pathlib.Path("foo.tif.back"), StatProxy(pathlib.Path("foo.tif.back"))
    )
    assert suffix_class(".txt.back").match(f3, StatProxy(f3))
    assert suffix_class(".back").match(f4, StatProxy(f4))
    assert suffix_class(".back").match(f2, StatProxy(f2))
    assert suffix_class(".back").match(f3, StatProxy(f3))
    assert not suffix_class(".back").match(f5, StatProxy(f5))
    assert suffix_class(".tar.zip").match(f6, StatProxy(f6))
    assert not suffix_class(".tar.zip").match(f1, StatProxy(f1))
    assert not suffix_class(".tar.zip").match(f2, StatProxy(f2))
