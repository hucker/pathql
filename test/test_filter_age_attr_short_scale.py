class TestStatProxy:
    def __init__(self, path, stat_result):
        self.path = path
        self._stat = stat_result
        self._stat_calls = 0

    def stat(self):
        self._stat_calls += 1
        return self._stat

    @property
    def stat_calls(self):
        return self._stat_calls


"""Deterministic tests for 1-second age behavior using injected stat_result objects.

These tests avoid filesystem platform differences (ctime semantics) by creating a
lightweight object with the expected `st_mtime`, `st_atime`, and `st_ctime`
attributes and passing it via the `stat_result` parameter to the filter's
`match()` method.
"""

import datetime as dt
import pathlib
import types

import pytest

from pathql.filters.age import AgeSeconds


def make_stat(
    st_mtime: float, st_atime: float | None = None, st_ctime: float | None = None
):
    # create a simple object with the required attributes
    obj = types.SimpleNamespace()
    obj.st_mtime = st_mtime
    obj.st_atime = st_atime if st_atime is not None else st_mtime
    obj.st_ctime = st_ctime if st_ctime is not None else st_mtime
    return obj


@pytest.mark.parametrize(
    "attr_name",
    [
        "st_atime",
        "st_mtime",
        "st_ctime",
    ],
)
@pytest.mark.parametrize(
    "offset,expected_age,msg",
    [
        (0.999999, 0, "just below 1 second should yield unit_age == 0"),
        (1.0, 1, "exactly 1 second should yield unit_age == 1"),
        (1.000001, 1, "just above 1 second should yield unit_age == 1"),
    ],
)
def test_age_seconds_boundaries(
    attr_name: str, offset: float, expected_age: int, msg: str
) -> None:
    """
    Test AgeSeconds filter at 1-second boundaries using injected stat_result.

    This tests verifies that just below the integer boundary yields the lower age,
    exactly at the boundary yields the expected age, and just above the boundary
    still yields the expected age.
    """

    # Arrange
    now = dt.datetime(2025, 10, 21, 12, 0, 0)

    def stat_for_attr(attr_name: str, ts: float):
        if "mtime" in attr_name or "mod" in attr_name:
            return make_stat(st_mtime=ts)
        if "atime" in attr_name or "access" in attr_name:
            return make_stat(st_mtime=now.timestamp(), st_atime=ts)
        # default to ctime/created
        return make_stat(st_mtime=now.timestamp(), st_ctime=ts)

    ts = (now - dt.timedelta(seconds=offset)).timestamp()
    st = stat_for_attr(attr_name, ts)
    f = AgeSeconds(attr=attr_name) == expected_age
    dummy_path = pathlib.Path("dummy")

    # Act & Assert
    assert f.match(
        path=dummy_path, now=now, stat_proxy=TestStatProxy(dummy_path, st)
    ), f"{attr_name}: {msg}"
