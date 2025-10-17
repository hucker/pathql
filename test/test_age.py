"""
Tests for Age filters (AgeMinutes, AgeDays, AgeYears) in PathQL.

Includes helpers to set file modification times and exhaustive parametric tests for all age filters and comparison operators.
"""
import os
import time
import operator
import pathlib
import pytest

from src.pathql.filters.age import AgeDays, AgeMinutes, AgeYears

def set_mtime_minutes_ago(path: pathlib.Path, minutes: float, now: float | None = None) -> None:
    """Set file mtime to N minutes ago."""
    if now is None:
        now = time.time()
    ago = now - (minutes * 60)
    os.utime(path, (ago, ago))

def set_mtime_hours_ago(path: pathlib.Path, hours: float, now: float | None = None) -> None:
    """Set file mtime to N hours ago."""
    if now is None:
        now = time.time()
    ago = now - (hours * 3600)
    os.utime(path, (ago, ago))

def set_mtime_days_ago(path: pathlib.Path, days: float, now: float | None = None) -> None:
    """Set file mtime to N days ago."""
    if now is None:
        now = time.time()
    ago = now - (days * 86400)
    os.utime(path, (ago, ago))

def set_mtime_years_ago(path: pathlib.Path, years: float, now: float | None = None) -> None:
    """Set file mtime to N years ago."""
    if now is None:
        now = time.time()
    ago = now - (years * 365.25 * 86400)
    os.utime(path, (ago, ago))




# Parameterized test for all age filters and operators
@pytest.mark.parametrize(
    "filter_cls,setter,unit",
    [
        (AgeMinutes, set_mtime_minutes_ago, 1),
        (AgeDays, set_mtime_days_ago, 1),
        (AgeYears, set_mtime_years_ago, 1),
    ]
)
@pytest.mark.parametrize(
    "op,expected_below,expected_exact,expected_above",
    [
        (operator.lt, True, False, False),
        (operator.le, True, True, False),
        (operator.eq, False, True, False),
        (operator.ge, False, True, True),
        (operator.gt, False, False, True),
        (operator.ne, True, False, True),
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
    Exhaustive parametric test for all age filters (minutes, days, years) and all comparison operators.

    For each filter and operator, this test sets the file's mtime to just below, exactly at,
    and just above the threshold (e.g., 1 minute, 1 day, 1 year) and asserts the expected
    result for the operator. This ensures:
            - Operator overloading works for <, <=, ==, >=, >, !=
            - Each filter correctly computes age in its unit
            - Edge cases at the threshold are handled correctly

    To add more time units (e.g., AgeSeconds), add to the filter_cls/setter/unit param list.
    To test more edge cases, adjust the values passed to the setter.

    This dense test provides full coverage for all filter/operator/unit combinations in a single place.
    """
    f = tmp_path / "test.txt"
    f.write_text("X")
    now = time.time()
    # Just below threshold
    setter(f, unit - 0.0001, now)
    assert op(filter_cls, unit).match(f, now=now) is expected_below
    # Exactly at threshold
    setter(f, unit, now)
    assert op(filter_cls, unit).match(f, now=now) is expected_exact
    # Just above threshold
    setter(f, unit + 0.0001, now)
    assert op(filter_cls, unit).match(f, now=now) is expected_above

