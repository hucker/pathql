"""
Tests for the requires_stat property of all PathQL filter classes.

Verifies that each filter class correctly reports whether it requires stat data, and that composite filters (And, Or, Not) propagate stat requirements as expected.
"""
import pathlib
import pytest
from pathql.filters.age import AgeMinutes, AgeHours, AgeDays, AgeYears
from pathql.filters.filedate import FileDate
from pathql.filters.size import Size
from pathql.filters.type import Type
from pathql.filters.suffix import Suffix
from pathql.filters.stem import Stem
from pathql.filters.file import File
from pathql.filters.base import AndFilter, OrFilter, NotFilter

# List of (filter class, expected requires_stat)
SIMPLE_FILTERS = [
    (AgeMinutes(lt=5), True),
    (AgeHours(gt=1), True),
    (AgeDays(eq=0), True),
    (AgeYears(ge=2), True),
    (FileDate(), True),
    (Size(op=lambda a, b: a > b, value=100), True),
    (Type().file, False),
    (Suffix("txt"), False),
    (Stem("foo"), False),
    (File("*.py"), False),
]

def test_requires_stat_simple():
    for filt, expected in SIMPLE_FILTERS:
        assert filt.requires_stat is expected, f"{type(filt).__name__} requires_stat should be {expected}"

def test_requires_stat_not():
    for filt, expected in SIMPLE_FILTERS:
        notf = NotFilter(filt)
        assert notf.requires_stat is expected, f"NotFilter({type(filt).__name__}) requires_stat should be {expected}"

def test_requires_stat_and_or():
    # All combinations of two filters
    for (f1, e1) in SIMPLE_FILTERS:
        for (f2, e2) in SIMPLE_FILTERS:
            andf = AndFilter(f1, f2)
            orf = OrFilter(f1, f2)
            expected = e1 or e2
            assert andf.requires_stat is expected, f"AndFilter({type(f1).__name__}, {type(f2).__name__}) requires_stat should be {expected}"
            assert orf.requires_stat is expected, f"OrFilter({type(f1).__name__}, {type(f2).__name__}) requires_stat should be {expected}"

@pytest.mark.parametrize("expr, expected", [
    # Single filters
    (AgeMinutes(lt=5), True),
    (Type().file, False),
    # Simple And/Or
    (AndFilter(AgeMinutes(lt=5), Type().file), True),
    (OrFilter(Type().file, Suffix("txt")), False),
    (OrFilter(Type().file, AgeMinutes(lt=5)), True),
    # Nested
    (AndFilter(OrFilter(Type().file, Suffix("txt")), NotFilter(File("*.py"))), False),
    (AndFilter(OrFilter(Type().file, AgeMinutes(lt=5)), NotFilter(File("*.py"))), True),
    (OrFilter(AndFilter(Type().file, Suffix("txt")), NotFilter(File("*.py"))), False),
    (OrFilter(AndFilter(Type().file, AgeMinutes(lt=5)), NotFilter(File("*.py"))), True),
])
def test_requires_stat_param(expr, expected):
    assert expr.requires_stat is expected

@pytest.mark.parametrize("expr, expected", [
    # Large expressions: if any subfilter requires stat, the whole expression does
    (AndFilter(
        OrFilter(Type().file, Suffix("txt")),
        AndFilter(File("*.py"), NotFilter(Type().file))
    ), False),
    (AndFilter(
        OrFilter(Type().file, AgeMinutes(lt=5)),
        AndFilter(File("*.py"), NotFilter(Type().file))
    ), True),
    (OrFilter(
        AndFilter(Type().file, Suffix("txt")),
        AndFilter(File("*.py"), NotFilter(Type().file))
    ), False),
    (OrFilter(
        AndFilter(Type().file, AgeMinutes(lt=5)),
        AndFilter(File("*.py"), NotFilter(Type().file))
    ), True),
    (AndFilter(
        OrFilter(Type().file, Suffix("txt")),
        AndFilter(File("*.py"), NotFilter(AgeMinutes(lt=5)))
    ), True),
])
def test_requires_stat_large_param(expr, expected):
    assert expr.requires_stat is expected
