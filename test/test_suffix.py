"""Tests for Suffix and Ext filters, including operator and multiple extension cases."""


import pathlib
import pytest
from pathql.filters.suffix import Suffix, Ext
from typing import Type


@pytest.fixture(params=[Suffix, Ext])
def suffix_cls_fixture(request: pytest.FixtureRequest) -> Type[Suffix | Ext]:
    """
    Fixture to parameterize tests with Suffix and Ext classes.
    """
    return request.param

def test_suffix_eq(suffix_cls_fixture: Type[Suffix | Ext]) -> None:
    """
    Test equality matching for Suffix and Ext filters.

    - Arrange: Create a file path.
    - Act: Apply equality filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f = pathlib.Path("foo.txt")

    # Act and Assert
    assert suffix_cls_fixture("txt").match(f)
    assert not suffix_cls_fixture("md").match(f)

def test_suffix_multiple(suffix_cls_fixture: Type[Suffix | Ext]) -> None:
    """
    Test multiple extension matching for Suffix and Ext filters.

    - Arrange: Create multiple file paths.
    - Act: Apply multiple extension filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.md")
    suffix_filter = suffix_cls_fixture(["txt", "md"])

    # Act and Assert
    assert suffix_filter.match(f1)
    assert suffix_filter.match(f2)

def test_suffix_case_insensitive(suffix_cls_fixture: Type[Suffix | Ext]) -> None:
    """
    Test case-insensitive matching for Suffix and Ext filters.

    - Arrange: Create a file path with uppercase extension.
    - Act: Apply case-insensitive filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f = pathlib.Path("foo.TXT")

    # Act and Assert
    assert suffix_cls_fixture("txt").match(f)
    assert suffix_cls_fixture("TXT").match(f)

def test_suffix_no_extension(suffix_cls_fixture: Type[Suffix | Ext]) -> None:
    """
    Test no-extension matching for Suffix and Ext filters.

    - Arrange: Create a file path with no extension.
    - Act: Apply filter.
    - Assert: Verify no match.
    """
    # Arrange
    f = pathlib.Path("foo")

    # Act and Assert
    assert not suffix_cls_fixture("txt").match(f)

def test_suffix_whitespace_split(suffix_cls_fixture: Type[Suffix | Ext]) -> None:
    """
    Test whitespace-split matching for Suffix and Ext filters.

    - Arrange: Create file paths with multiple extensions.
    - Act: Apply whitespace-split filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.bmp")
    suffix_filter = suffix_cls_fixture("txt bmp")

    # Act and Assert
    assert suffix_filter.match(f1)
    assert suffix_filter.match(f2)
    assert not suffix_filter.match(pathlib.Path("baz.md"))

def test_suffix_nosplit(suffix_cls_fixture: Type[Suffix | Ext]) -> None:
    """
    Test no-split matching for Suffix and Ext filters.

    - Arrange: Create a file path with a compound extension.
    - Act: Apply no-split filter.
    - Assert: Verify matching results.
    """
    # Arrange
    f = pathlib.Path("foo.txt bmp")
    suffix_filter = suffix_cls_fixture("txt bmp", nosplit=True)
    suffix_filter2 = suffix_cls_fixture("txt bmp")

    # Act and Assert
    assert suffix_filter.match(f)
    assert not suffix_filter2.match(f)

def test_suffix_dot_prefix_equivalence(suffix_cls_fixture: Type[Suffix | Ext]) -> None:
    """
    Test that Suffix/Ext treat '.jpg' and 'jpg' identically.

    - Arrange: Create file paths with .jpg extension.
    - Act: Apply filters with and without leading dot.
    - Assert: Both match identically.
    """
    # Arrange
    f = pathlib.Path("image.jpg")
    f_upper = pathlib.Path("image.JPG")

    # Act & Assert
    assert suffix_cls_fixture("jpg").match(f)
    assert suffix_cls_fixture(".jpg").match(f)
    assert suffix_cls_fixture(["jpg"]).match(f)
    assert suffix_cls_fixture([".jpg"]).match(f)
    assert suffix_cls_fixture("jpg").match(f_upper)
    assert suffix_cls_fixture(".jpg").match(f_upper)
    # Mixed list
    assert suffix_cls_fixture([".jpg", "txt"]).match(f)
    assert suffix_cls_fixture(["jpg", ".txt"]).match(f)
    # Curly-brace expansion
    assert suffix_cls_fixture("{.jpg,.png}").match(f)
    assert suffix_cls_fixture("{jpg,png}").match(f)
    # Negative case
    assert not suffix_cls_fixture("png").match(f)
    assert not suffix_cls_fixture([".png"]).match(f)

def test_suffix_multi_part_extensions(suffix_cls_fixture: Type[Suffix | Ext]) -> None:
    """
    Test that Suffix/Ext can match multi-part extensions like '.tar.gz', '.tif.back'.

    - Arrange: Create file paths with multi-part extensions.
    - Act: Apply filters with multi-part extension patterns.
    - Assert: Only correct files match.
    """
    # Arrange
    f1 = pathlib.Path("archive.tar.gz")
    f2 = pathlib.Path("image.tif.back")
    f3 = pathlib.Path("foo.txt.back")
    f4 = pathlib.Path("foo.back")
    f5 = pathlib.Path("foo.tif")
    f6 = pathlib.Path("foo.tar.zip")

    # Act & Assert
    assert suffix_cls_fixture(".tar.gz").match(f1)
    assert not suffix_cls_fixture(".tar.gz").match(f2)
    assert suffix_cls_fixture(".tar.gz").match(pathlib.Path("foo.bar.tar.gz"))
    assert suffix_cls_fixture(".tif.back").match(f2)
    assert suffix_cls_fixture(".tif.back").match(pathlib.Path("foo.tif.back"))
    assert suffix_cls_fixture(".txt.back").match(f3)
    assert suffix_cls_fixture(".back").match(f4)
    assert suffix_cls_fixture(".back").match(f2)
    assert suffix_cls_fixture(".back").match(f3)
    assert not suffix_cls_fixture(".back").match(f5)
    assert suffix_cls_fixture(".tar.zip").match(f6)
    assert not suffix_cls_fixture(".tar.zip").match(f1)
    assert not suffix_cls_fixture(".tar.zip").match(f2)
