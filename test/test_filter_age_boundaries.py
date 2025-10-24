"""Boundary tests for Age filters: check just-below, exact, and just-above unit boundaries.

These tests set file mtimes precisely using `os.utime` with timestamps computed
from a fixed `now` datetime and exercise AgeMinutes, AgeHours, AgeDays, and
AgeYears for the boundary values 0 and 1 unit.
"""

import datetime as dt
import os
import pathlib

import pytest

from pathql.filters.age import AgeDays, AgeHours, AgeMinutes, AgeYears


def set_mtime(path: pathlib.Path, when: dt.datetime) -> None:
    ts = when.timestamp()
    os.utime(path, (ts, ts))


@pytest.mark.parametrize(
    "filter_cls,unit_seconds",
    [
        (AgeMinutes, 60),
        (AgeHours, 3600),
        (AgeDays, 86400),
        (AgeYears, 86400 * 365.25),
    ],
)
def test_age_boundaries(
    tmp_path: pathlib.Path, filter_cls: type, unit_seconds: float
) -> None:
    f = tmp_path / "b.txt"
    f.write_text("x")
    now = dt.datetime.now()

    # Just below 1 unit: now - (1 unit - small_delta)
    small_delta = 1e-6  # one microsecond-ish in seconds
    just_below = now - dt.timedelta(seconds=(unit_seconds - small_delta))
    set_mtime(f, just_below)
    # unit_age floors to 0
    from pathql.filters.stat_proxy import StatProxy

    assert (filter_cls() == 0).match(f, stat_proxy=StatProxy(f), now=now)
    assert not (filter_cls() == 1).match(f, stat_proxy=StatProxy(f), now=now)

    # Exactly at 1 unit boundary
    exact = now - dt.timedelta(seconds=unit_seconds)
    set_mtime(f, exact)
    # unit_age == 1
    assert not (filter_cls() == 0).match(f, stat_proxy=StatProxy(f), now=now)
    assert (filter_cls() == 1).match(f, stat_proxy=StatProxy(f), now=now)

    # Just above 1 unit (slightly more than 1 unit ago)
    just_above = now - dt.timedelta(seconds=(unit_seconds + small_delta))
    set_mtime(f, just_above)
    # unit_age == 1
    assert not (filter_cls() == 0).match(f, stat_proxy=StatProxy(f), now=now)
    assert (filter_cls() == 1).match(f, stat_proxy=StatProxy(f), now=now)
