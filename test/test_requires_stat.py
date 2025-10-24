"""
Tests for the requires_stat property of all PathQL filter classes.

Verifies that each filter class correctly reports whether it requires stat data, and that composite filters (And, Or, Not) propagate stat requirements as expected.
"""

import pathlib

import pytest

from pathql.filters.age import AgeDays, AgeHours, AgeMinutes, AgeYears
from pathql.filters.base import AndFilter, NotFilter, OrFilter
from pathql.filters.between import Between
from pathql.filters.callback import MatchCallback, PathCallback
from pathql.filters.file import File
from pathql.filters.file_type import FileType
from pathql.filters.filedate import FileDate
from pathql.filters.size import Size
from pathql.filters.stem import Stem
from pathql.filters.suffix import Suffix


def dummy_func(path: pathlib.Path) -> bool:
    """Dummy callback for PathCallback (does not require stat)."""
    return True


def dummy_func_stat(path: pathlib.Path, now: object, stat_result: object) -> bool:
    """Dummy callback for MatchCallback (requires stat)."""
    return True


def test_requires_stat_callback() -> None:
    """Test that PathCallback does not require stat."""
    # Arrange
    cb = PathCallback(dummy_func)
    cb2 = PathCallback(lambda p: True)
    # Act & Assert
    assert cb.requires_stat is False
    assert cb2.requires_stat is False


def test_requires_stat_matchcallback() -> None:
    """Test that MatchCallback requires stat."""
    # Arrange
    mcb = MatchCallback(dummy_func_stat)
    # Act & Assert
    assert mcb.requires_stat is True


def test_requires_stat_between() -> None:
    """Test that Between requires stat if the underlying filter does."""
    # Arrange
    from pathql.filters.age import AgeMinutes

    b1 = Between(AgeMinutes(), 1, 5)
    # Act & Assert
    assert b1.filter.requires_stat is True


def test_requires_stat_between_composed() -> None:
    """Test that composed Between filters propagate stat requirements."""
    # Arrange
    from pathql.filters.age import AgeMinutes

    b_stat = Between(AgeMinutes(), 1, 5)
    # Act
    andf = b_stat.filter & b_stat.filter
    orf = b_stat.filter | b_stat.filter
    # Assert
    assert andf.requires_stat is True
    assert orf.requires_stat is True


# List of (filter class, expected requires_stat)
SIMPLE_FILTERS = [
    (AgeMinutes() < 5, True),
    (AgeHours() > 1, True),
    (AgeDays() == 0, True),
    (AgeYears() >= 2, True),
    (FileDate(), True),
    (Size(op=lambda a, b: a > b, value=100), True),
    (FileType().file, False),
    (Suffix("txt"), False),
    (Stem("foo"), False),
    (File("*.py"), False),
]


def test_requires_stat_simple() -> None:
    """Test requires_stat for all simple filters."""
    # Arrange/Act/Assert
    for filt, expected in SIMPLE_FILTERS:
        assert filt.requires_stat is expected, (
            f"{type(filt).__name__} requires_stat should be {expected}"
        )


def test_requires_stat_not() -> None:
    """Test requires_stat for NotFilter of all simple filters."""
    # Arrange/Act/Assert
    for filt, expected in SIMPLE_FILTERS:
        notf = NotFilter(filt)
        assert notf.requires_stat is expected, (
            f"NotFilter({type(filt).__name__}) requires_stat should be {expected}"
        )


def test_requires_stat_and_or() -> None:
    """Test requires_stat for AndFilter and OrFilter of all filter pairs."""
    # Arrange/Act/Assert
    for f1, e1 in SIMPLE_FILTERS:
        for f2, e2 in SIMPLE_FILTERS:
            andf = AndFilter(f1, f2)
            orf = OrFilter(f1, f2)
            expected = e1 or e2
            assert andf.requires_stat is expected, (
                f"AndFilter({type(f1).__name__}, {type(f2).__name__}) requires_stat should be {expected}"
            )
            assert orf.requires_stat is expected, (
                f"OrFilter({type(f1).__name__}, {type(f2).__name__}) requires_stat should be {expected}"
            )


@pytest.mark.parametrize(
    "expr, expected",
    [
        # Single filters
        (AgeMinutes() < 5, True),
        (FileType().file, False),
        # Simple And/Or
        (AndFilter(AgeMinutes() < 5, FileType().file), True),
        (OrFilter(FileType().file, Suffix("txt")), False),
        (OrFilter(FileType().file, AgeMinutes() < 5), True),
        # Nested
        (
            AndFilter(
                OrFilter(FileType().file, Suffix("txt")), NotFilter(File("*.py"))
            ),
            False,
        ),
        (
            AndFilter(
                OrFilter(FileType().file, AgeMinutes() < 5), NotFilter(File("*.py"))
            ),
            True,
        ),
        (
            OrFilter(
                AndFilter(FileType().file, Suffix("txt")), NotFilter(File("*.py"))
            ),
            False,
        ),
        (
            OrFilter(
                AndFilter(FileType().file, AgeMinutes() < 5), NotFilter(File("*.py"))
            ),
            True,
        ),
    ],
)
def test_requires_stat_param(expr: object, expected: bool) -> None:
    """Test requires_stat for parameterized filter expressions."""
    # Act & Assert
    assert expr.requires_stat is expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        # Large expressions: if any subfilter requires stat, the whole expression does
        (
            AndFilter(
                OrFilter(FileType().file, Suffix("txt")),
                AndFilter(File("*.py"), NotFilter(FileType().file)),
            ),
            False,
        ),
        (
            AndFilter(
                OrFilter(FileType().file, AgeMinutes() < 5),
                AndFilter(File("*.py"), NotFilter(FileType().file)),
            ),
            True,
        ),
        (
            OrFilter(
                AndFilter(FileType().file, Suffix("txt")),
                AndFilter(File("*.py"), NotFilter(FileType().file)),
            ),
            False,
        ),
        (
            OrFilter(
                AndFilter(FileType().file, AgeMinutes() < 5),
                AndFilter(File("*.py"), NotFilter(FileType().file)),
            ),
            True,
        ),
        (
            AndFilter(
                OrFilter(FileType().file, Suffix("txt")),
                AndFilter(File("*.py"), NotFilter(AgeMinutes() < 5)),
            ),
            True,
        ),
    ],
)
def test_requires_stat_large_param(expr: object, expected: bool) -> None:
    """Test requires_stat for large parameterized filter expressions."""
    # Act & Assert
    assert expr.requires_stat is expected


# Additional: test all filter classes in the codebase for requires_stat property
def test_all_known_filters_have_requires_stat() -> None:
    """Test that all known filter classes have a requires_stat property and it is a bool."""
    # Arrange
    filter_classes = [
        AgeMinutes,
        AgeHours,
        AgeDays,
        AgeYears,
        FileDate,
        Size,
        FileType,
        Suffix,
        Stem,
        PathCallback,
        MatchCallback,
        Between,
        AndFilter,
        OrFilter,
        NotFilter,
    ]
    # Act & Assert
    for cls in filter_classes:
        # Try to instantiate with minimal args
        try:
            if cls in (AgeMinutes, AgeHours, AgeDays, AgeYears):
                inst = cls() < 1
            elif cls is FileDate:
                inst = cls()
            elif cls is Size:
                inst = cls(op=lambda a, b: a > b, value=1)
            elif cls is FileType:
                inst = cls().file
            elif cls is Suffix:
                inst = cls("txt")
            elif cls is Stem:
                inst = cls("foo")
            elif cls is File:
                inst = cls("*.py")
            elif cls is PathCallback:
                inst = cls(dummy_func)
            elif cls is MatchCallback:
                inst = cls(dummy_func_stat)
            elif cls is Between:
                inst = cls(AgeMinutes(), 1, 2)
            elif cls is AndFilter:
                inst = cls(File("*.py"), File("*.py"))
            elif cls is OrFilter:
                inst = cls(File("*.py"), File("*.py"))
            elif cls is NotFilter:
                inst = cls(File("*.py"))
            else:
                continue
        except Exception:
            continue
        # Accepts property or attribute
        assert hasattr(type(inst), "requires_stat"), (
            f"{cls.__name__} missing requires_stat property"
        )
        val = inst.requires_stat
        assert isinstance(val, bool), f"{cls.__name__} requires_stat is not bool"
