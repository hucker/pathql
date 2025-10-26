"""
Tests for All, Any, and Every filter combinators in PathQL.

Covers:
- Single, double, and triple filter cases
- Both positional and iterable argument forms
- Short-circuiting behavior (using call counters)
"""

import pathlib
from typing import List

import pytest

from pathql.filters.alias import DatetimeOrNone
from pathql.filters.base import All, Any, AllowAll, Filter, StatProxyOrNone


class TrueFilter(Filter):
    def match(self, path: pathlib.Path, stat_proxy:StatProxyOrNone=None, now:DatetimeOrNone =None) -> bool:
        """All files match"""
        return True

class FalseFilter(Filter):
    def match(self, path: pathlib.Path, stat_proxy:StatProxyOrNone=None, now:DatetimeOrNone=None) -> bool:
        """No files match"""
        return False

class SideEffectFilter(Filter):
    """
    Filter that returns a fixed result and counts how many times match() is called.
    """
    def __init__(self, result: bool):
        self.result = result
        self.call_count = 0

    def match(self, path: pathlib.Path, stat_proxy:StatProxyOrNone=None, now:DatetimeOrNone=None) -> bool:
        self.call_count += 1
        return self.result


@pytest.mark.parametrize(
    "combinator, args, expected",
    [
        # Always all files to matche
        (AllowAll, [], True),

        # All: single filter
        (All, [TrueFilter()], True),
        (All, [FalseFilter()], False),

        # All: two filters
        (All, [TrueFilter(), TrueFilter()], True),
        (All, [TrueFilter(), FalseFilter()], False),
        (All, [FalseFilter(), TrueFilter()], False),
        (All, [FalseFilter(), FalseFilter()], False),

        # All: three filters
        (All, [TrueFilter(), TrueFilter(), TrueFilter()], True),
        (All, [TrueFilter(), TrueFilter(), FalseFilter()], False),
        (All, [FalseFilter(), TrueFilter(), TrueFilter()], False),

        # Any: single filter
        (Any, [TrueFilter()], True),
        (Any, [FalseFilter()], False),

        # Any: two filters
       (Any, [TrueFilter(), FalseFilter()], True),
        (Any, [FalseFilter(), TrueFilter()], True),
        (Any, [FalseFilter(), FalseFilter()], False),

        # Any: three filters
        (Any, [TrueFilter(), TrueFilter(), TrueFilter()], True),
        (Any, [TrueFilter(), TrueFilter(), FalseFilter()], True),
        (Any, [FalseFilter(), FalseFilter(), TrueFilter()], True),
        (Any, [FalseFilter(), FalseFilter(), FalseFilter()], False),
    ]
)
@pytest.mark.parametrize("form", ["positional", "iterable"])
def test_combinator_filters(combinator, args, expected, form):
    """
    Test All, Any, and Every combinators with 1, 2, and 3 filters,
    using both positional and iterable forms.
    """
    # Arrange
    dummy_path = pathlib.Path("dummy.txt")
    # Act
    if combinator is AllowAll:
        value_filter: Filter = combinator()
    elif form == "positional":
        value_filter: Filter = combinator(*args)
    else:
        value_filter: Filter = combinator(args)
    actual = value_filter.match(dummy_path)
    # Assert
    assert actual == expected, (
        f"{combinator.__name__}({args}, form={form}) returned {actual}, expected {expected}"
    )

@pytest.mark.parametrize(
    "combinator, results, expected_result, expected_calls",
    [
        # All short-circuit: stops at first False
        (All, [True, False, True], False, [1, 1, 0]),
        (All, [True, True, False], False, [1, 1, 1]),
        (All, [True, True, True], True, [1, 1, 1]),
        (All, [False, True, True], False, [1, 0, 0]),
        # Any short-circuit: stops at first True
        (Any, [False, True, True], True, [1, 1, 0]),
        (Any, [False, False, True], True, [1, 1, 1]),
        (Any, [True, False, True], True, [1, 0, 0]),
        (Any, [False, False, False], False, [1, 1, 1]),
        (Any, [True, True, True], True, [1, 0, 0]),
    ]
)
def test_short_circuiting(combinator:Filter, results: list[bool], expected_result: bool, expected_calls: list[int]):
    """
    Parameterized test for short-circuiting in All and Any combinators.
    Checks that only the necessary filters are called.
    """
    # Arrange
    filters:List[Filter] = [SideEffectFilter(r) for r in results]
    value_filter: Filter = combinator(*filters)
    # Act
    result:bool = value_filter.match(pathlib.Path("dummy.txt"))
    # Assert
    assert result == expected_result
    for idx, (filter, expected_count) in enumerate(zip(filters, expected_calls)):
        assert filter.call_count == expected_count, (
            f"Filter {idx} call_count={filt.call_count}, expected {expected_count}"
        )

def test_any_single_filter_count():
    """
    Test that Any with a single filter only calls that filter once.
    """
    # Arrange
    f1 = SideEffectFilter(True)
    value_filter: Filter = Any(f1)
    # Act
    result = value_filter.match(pathlib.Path("dummy.txt"))
    # Assert
    assert result is True
    assert f1.call_count == 1, "Single filter should be called once"
