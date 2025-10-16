
import os
import time
import pytest
import operator
from pathql.filters.age import AgeDays, AgeMinutes, AgeYears

def set_mtime_minutes_ago(path, minutes, now=None):
    if now is None:
        now = time.time()
    ago = now - (minutes * 60)
    os.utime(path, (ago, ago))

def set_mtime_hours_ago(path, hours, now=None):
    if now is None:
        now = time.time()
    ago = now - (hours * 3600)
    os.utime(path, (ago, ago))

def set_mtime_days_ago(path, days, now=None):
    if now is None:
        now = time.time()
    ago = now - (days * 86400)
    os.utime(path, (ago, ago))

def set_mtime_years_ago(path, years, now=None):
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
def test_age_thresholds(tmp_path, filter_cls, setter, unit, op, expected_below, expected_exact, expected_above):
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

