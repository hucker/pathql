"""Tests for Age filters: minutes, hours, days, and years."""

import datetime as dt
import operator
import os
import pathlib
from typing import Callable,Any

import pytest

from pathql.filters.age import AgeDays, AgeHours, AgeMinutes, AgeYears
from pathql.filters.alias import DatetimeOrNone
from pathql.filters.base import Filter


def set_mtime_minutes_ago(
    path: pathlib.Path,
    minutes: float,
    now: dt.datetime | None = None,
) -> None:
    """Set file mtime to N minutes ago using a datetime object."""
    if now is None:
        now = dt.datetime.now()
    ago = now - dt.timedelta(minutes=minutes)
    ts = ago.timestamp()
    os.utime(path, (ts, ts))


def set_mtime_hours_ago(
    path: pathlib.Path,
    hours: float,
    now: dt.datetime | None = None,
) -> None:
    """Set file mtime to N hours ago using a datetime object."""
    if now is None:
        now = dt.datetime.now()
    ago = now - dt.timedelta(hours=hours)
    ts = ago.timestamp()
    os.utime(path, (ts, ts))


def set_mtime_days_ago(
    path: pathlib.Path,
    days: float,
    now: dt.datetime | None = None,
) -> None:
    """Set file mtime to N days ago using a datetime object."""
    if now is None:
        now = dt.datetime.now()
    ago = now - dt.timedelta(days=days)
    ts = ago.timestamp()
    os.utime(path, (ts, ts))


def set_mtime_years_ago(
    path: pathlib.Path,
    years: float,
    now: dt.datetime | None = None,
) -> None:
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
    ],
)
@pytest.mark.parametrize(
    "op,expected_below,expected_exact,expected_above",
    [
        (operator.lt, True, False, False),
        # With integer unit rounding, 'just above' the threshold floors to the same unit as exact
        (operator.le, True, True, True),
        (operator.ge, False, True, True),
        (operator.gt, False, False, False),
    ],
)
def test_age_thresholds(
    tmp_path: pathlib.Path,
    filter_cls: type[Filter],
    setter: Callable[[pathlib.Path, float, dt.datetime | None], None],
    unit: float,
    op: Callable[[Filter, float], Filter],
    expected_below: bool,
    expected_exact: bool,
    expected_above: bool,
) -> None:
    """Parametric test across age units and comparison operators (below/equal/above)."""
    # Arrange
    f = tmp_path / "test.txt"
    f.write_text("X")
    now = dt.datetime.now()  # Use datetime, not time.time()

    from pathql.filters.stat_proxy import StatProxy

    if filter_cls is AgeYears:
        # Use integer days to avoid leap year ambiguity
        setter(f, 364 / 365, now)  # Just below 1 year
        result_below = op(filter_cls(), unit).match(f, stat_proxy=StatProxy(f), now=now)
        assert result_below is expected_below

        setter(f, 1, now)  # Exactly 1 year
        result_exact = op(filter_cls(), unit).match(f, stat_proxy=StatProxy(f), now=now)
        assert result_exact is expected_exact

        setter(f, 366 / 365, now)  # Just above 1 year
        result_above = op(filter_cls(), unit).match(f, stat_proxy=StatProxy(f), now=now)
        assert result_above is expected_above
    else:
        # Act & Assert: Just below threshold
        setter(f, unit - 0.0001, now)
        result_below = op(filter_cls(), unit).match(f, stat_proxy=StatProxy(f), now=now)
        assert result_below is expected_below

        setter(f, unit, now)
        result_exact = op(filter_cls(), unit).match(f, stat_proxy=StatProxy(f), now=now)
        assert result_exact is expected_exact

        setter(f, unit + 0.0001, now)
        result_above = op(filter_cls(), unit).match(f, stat_proxy=StatProxy(f), now=now)
        assert result_above is expected_above


@pytest.mark.parametrize(
    "filter_cls,setter,unit",
    [
        (AgeMinutes, set_mtime_minutes_ago, 1),
        (AgeHours, set_mtime_hours_ago, 1),
        (AgeDays, set_mtime_days_ago, 1),
        (AgeYears, set_mtime_years_ago, 1),
    ],
)
def test_age_filter_eq_ne_behaviour(
    tmp_path: pathlib.Path,
    filter_cls: type[Filter],
    setter: Callable[[pathlib.Path, float, DatetimeOrNone], None],
    unit: float,
) -> None:
    """Equality and inequality compare integer unit-aged values (rounded/floored).

    For example, AgeDays == 0 matches files with age >= 0 and < 1 day.
    """
    # Arrange
    f: pathlib.Path = tmp_path / "test.txt"
    f.write_text("X")
    now: DatetimeOrNone = dt.datetime.now()

    # Newly created file -> unit_age == 0
    setter(f, 0, now)
    from pathql.filters.stat_proxy import StatProxy

    assert operator.eq(filter_cls(), 0).match(f, stat_proxy=StatProxy(f), now=now)
    assert not operator.ne(filter_cls(), 0).match(f, stat_proxy=StatProxy(f), now=now)

    setter(f, unit, now)
    assert operator.eq(filter_cls(), 1).match(f, stat_proxy=StatProxy(f), now=now)
    assert not operator.ne(filter_cls(), 1).match(f, stat_proxy=StatProxy(f), now=now)
    assert operator.eq(filter_cls(), 1).match(f, stat_proxy=StatProxy(f), now=now)
    assert not operator.ne(filter_cls(), 1).match(f, stat_proxy=StatProxy(f), now=now)

def test_age_filter_missing_stat_proxy():
    """Raise TypeError if filter is not fully specified."""
    # Arrange
    f = pathlib.Path("foo.txt")
    age_filter = AgeMinutes(10)
    # Act & Assert
    with pytest.raises(TypeError, match="filter not fully specified"):
        age_filter.match(f, stat_proxy=None)

@pytest.mark.parametrize("filter_cls", [AgeMinutes, AgeHours, AgeDays, AgeYears])
@pytest.mark.parametrize("bad_value", [1.5, "10", None, [10], {"val": 10}])
def test_age_filter_invalid_threshold_type(filter_cls, bad_value):
    """Raise TypeError for non-integer threshold values."""
    # Arrange
    f = filter_cls(bad_value)
    # Act & Assert
    with pytest.raises(TypeError, match="filter not fully specified"):
        f.match(pathlib.Path("foo.txt"), stat_proxy=None)

