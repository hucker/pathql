"""Deterministic tests for 1-second age behaviour using injected stat_result objects.

These tests avoid filesystem platform differences (ctime semantics) by creating a
lightweight object with the expected `st_mtime`, `st_atime`, and `st_ctime`
attributes and passing it via the `stat_result` parameter to the filter's
`match()` method.
"""
import datetime as dt
import types
import pytest

from pathql.filters.age import AgeBase


class AgeSeconds(AgeBase):
    unit_seconds = 1.0


def make_stat(st_mtime: float, st_atime: float | None = None, st_ctime: float | None = None):
    # create a simple object with the required attributes
    obj = types.SimpleNamespace()
    obj.st_mtime = st_mtime
    obj.st_atime = st_atime if st_atime is not None else st_mtime
    obj.st_ctime = st_ctime if st_ctime is not None else st_mtime
    return obj


@pytest.mark.parametrize("attr_name,stat_attr", [
    ("modified", "st_mtime"),
    ("accessed", "st_atime"),
    ("created", "st_ctime"),
])
def test_age_seconds_boundaries(attr_name: str, stat_attr: str) -> None:
    now = dt.datetime(2025, 10, 21, 12, 0, 0)

    # just-below 1 second: age < 1 -> unit_age == 0
    just_below_ts = (now - dt.timedelta(seconds=0.000001)).timestamp()
    st = make_stat(st_mtime=just_below_ts)
    f = AgeSeconds(attr=attr_name) == 0
    assert f.match(path=None, now=now, stat_result=st)

    # exactly 1 second ago -> unit_age == 1
    exact_ts = (now - dt.timedelta(seconds=1)).timestamp()
    st = make_stat(st_mtime=exact_ts)
    f = AgeSeconds(attr=attr_name) == 1
    assert f.match(path=None, now=now, stat_result=st)

    # just-above 1 second (1.000001) -> unit_age == 1
    just_above_ts = (now - dt.timedelta(seconds=1.000001)).timestamp()
    st = make_stat(st_mtime=just_above_ts)
    f = AgeSeconds(attr=attr_name) == 1
    assert f.match(path=None, now=now, stat_result=st)
