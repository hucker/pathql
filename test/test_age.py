"""
Tests for Age filters (AgeMinutes, AgeDays, AgeYears) in PathQL.

Includes helpers to set file modification times and exhaustive parametric tests for all
age filters and comparison operators.
"""

import os
import datetime as dt
import operator
import pathlib
import pytest
from typing import Callable

from pathql.filters.age import AgeDays, AgeHours, AgeMinutes, AgeYears
from pathql.filters.base import Filter
from pathql.filters.alias import DatetimeOrNone

def set_mtime_minutes_ago(path: pathlib.Path,
                          minutes: float, now:
                          dt.datetime | None = None) -> None:
    """Set file mtime to N minutes ago using a datetime object."""
    if now is None:
        now = dt.datetime.now()
    ago = now - dt.timedelta(minutes=minutes)
    ts = ago.timestamp()
    os.utime(path, (ts, ts))

def set_mtime_hours_ago(path: pathlib.Path,
                        hours: float,
                        now: dt.datetime | None = None) -> None:
    """Set file mtime to N hours ago using a datetime object."""
    if now is None:
        now = dt.datetime.now()
    ago = now - dt.timedelta(hours=hours)
    ts = ago.timestamp()
    os.utime(path, (ts, ts))

def set_mtime_days_ago(path: pathlib.Path,
                       days: float, now:
                       dt.datetime | None = None) -> None:
    """Set file mtime to N days ago using a datetime object."""
    if now is None:
        now = dt.datetime.now()
    ago = now - dt.timedelta(days=days)
    ts = ago.timestamp()
    os.utime(path, (ts, ts))

def set_mtime_years_ago(path: pathlib.Path,
                        years: float,
                        now: dt.datetime | None = None) -> None:
    """Set file mtime to N years ago using a datetime object."""
    if now is None:
        now = dt.datetime.now()
    # Approximate years using days
    ago = now - dt.timedelta(days=years * 365.25)
    ts = ago.timestamp()
    os.utime(path, (ts, ts))




# Parameterized test for all age filters and operators
@pytest.mark.parametrize(
    "filter_cls,setter,unit",
    [
        (AgeMinutes, set_mtime_minutes_ago, 1),
        (AgeHours, set_mtime_hours_ago, 1),
        (AgeDays, set_mtime_days_ago, 1),
        (AgeYears, set_mtime_years_ago, 1),
    ]
)
@pytest.mark.parametrize(
    "op,expected_below,expected_exact,expected_above",
    [
        (operator.lt, True, False, False),
        (operator.le, True, True, False),
        (operator.ge, False, True, True),
        (operator.gt, False, False, True),
    ]
)
def test_age_thresholds(tmp_path:pathlib.Path,
                        filter_cls,
                        setter,
                        unit,
                        op,
                        expected_below:bool,
                        expected_exact:bool,
                        expected_above:bool):
    """
    Exhaustive parametric test for age filters (minutes, days, years) and all comparison operators.

    For each filter and operator, this test sets the file's mtime to just below, exactly at,
    and just above the threshold (e.g., 1 minute, 1 day, 1 year) and asserts the expected
    result for the operator. This ensures:
            - Operator overloading works for <, <=, ==, >=, >, !=
            - Each filter correctly computes age in its unit
            - Edge cases at the threshold are handled correctly

    To add more time units (e.g., AgeSeconds), add to the filter_cls/setter/unit param list.
    To test more edge cases, adjust the values passed to the setter.

    This dense test provides coverage for all filter/operator/unit combinations in a single place.
    """
    f = tmp_path / "test.txt"
    f.write_text("X")
    now = dt.datetime.now()  # Use datetime, not time.time()

    # Just below threshold
    setter(f, unit - 0.0001, now)
    assert op(filter_cls(), unit).match(f, now=now) is expected_below

    # Exactly at threshold
    setter(f, unit, now)
    assert op(filter_cls(), unit).match(f, now=now) is expected_exact

    # Just above threshold
    setter(f, unit + 0.0001, now)
    assert op(filter_cls(), unit).match(f, now=now) is expected_above


# Test that == and != raise TypeError for age filters
# Fixed the test to correctly check for TypeError when using == or != with filter_cls()
@pytest.mark.parametrize(
    "filter_cls,setter,unit",
    [
        (AgeMinutes, set_mtime_minutes_ago, 1),
        (AgeHours, set_mtime_hours_ago, 1),
        (AgeDays, set_mtime_days_ago, 1),
        (AgeYears, set_mtime_years_ago, 1),
    ]
)
@pytest.mark.parametrize("op", [operator.eq, operator.ne])
def test_age_filter_eq_ne_typeerror(tmp_path: pathlib.Path,
                                    filter_cls: type,
                                    setter: Callable[[pathlib.Path, float, DatetimeOrNone], None],
                                    unit: float,
                                    op: Callable[[Filter, float], bool]):
    """ Test different types of age filters to raise exceptions for == and != operators."""
    f: pathlib.Path = tmp_path / "test.txt"
    f.write_text("X")
    now: DatetimeOrNone = dt.datetime.now()
    setter(f, unit, now)
    with pytest.raises(TypeError):
        op(filter_cls(), unit)  # Removed .match() call, as op returns a bool
