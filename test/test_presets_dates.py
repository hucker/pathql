"""Tests for PathQL date-based preset filters."""
import os
import tempfile
import pathlib
import typing
import datetime as dt
import pytest
from unittest.mock import MagicMock
from pathql.filters.base import Filter
from pathql.presets.dates import (
    modified_this_hour, modified_today, modified_this_month, modified_this_year,
    created_this_hour, created_today, created_this_month, created_this_year,
    modified_yesterday, created_yesterday,
    modified_this_minute, created_this_minute
)
@pytest.mark.parametrize(
    "preset_func, offset, should_match",
    [
        (modified_this_hour, dt.timedelta(minutes=0), True),
        (modified_today, dt.timedelta(hours=0), True),
        (modified_this_month, dt.timedelta(days=0), True),
        (modified_this_year, dt.timedelta(days=0), True),
        (modified_this_hour, dt.timedelta(hours=1), False),
        (modified_today, dt.timedelta(days=1), False),
        (modified_this_month, dt.timedelta(days=32), False),
        (modified_this_year, dt.timedelta(days=366), False),
    ]
)
def test_modified_presets(
    file_and_times: tuple[pathlib.Path, dt.datetime],
    preset_func: typing.Callable[[dt.datetime | None], Filter],
    offset: dt.timedelta,
    should_match: bool
) -> None:
    """Test modified_* presets for correct match behavior."""
    fpath, mtime = file_and_times
    now: dt.datetime = mtime + offset
    stat = fpath.stat()
    preset: Filter = preset_func(now)
    result = preset.match(fpath, now=now.timestamp(), stat_result=stat)
    assert result is should_match, (
        f"Preset {preset_func.__name__} with now={now} (mtime={mtime}) expected {should_match} but got {result}"
    )

def set_file_mtime(path: pathlib.Path, mtime: float) -> None:
    """Set the modification time of a file."""
    os.utime(path, (mtime, mtime))

@pytest.fixture(scope="module")
def file_and_times() -> typing.Generator[tuple[pathlib.Path, dt.datetime], None, None]:
    """Fixture yielding a file and its mtime for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = pathlib.Path(tmpdir) / "testfile.txt"
        fpath.write_text("test")
        stat = fpath.stat()
        ctime = dt.datetime.fromtimestamp(stat.st_ctime)
        mtime = ctime - dt.timedelta(hours=1)
        set_file_mtime(fpath, mtime.timestamp())
        yield fpath, mtime


@pytest.mark.parametrize(
    "preset_func, offset, should_match",
    [
        (created_this_hour, dt.timedelta(minutes=0), True),
        (created_today, dt.timedelta(hours=0), True),
        (created_this_month, dt.timedelta(days=0), True),
        (created_this_year, dt.timedelta(days=0), True),
        (created_this_hour, dt.timedelta(hours=1), False),
        (created_today, dt.timedelta(days=1), False),
        (created_this_month, dt.timedelta(days=32), False),
        (created_this_year, dt.timedelta(days=366), False),
    ]
)
def test_created_presets(
    file_and_times: tuple[pathlib.Path, dt.datetime],
    preset_func: typing.Callable[[dt.datetime | None], Filter],
    offset: dt.timedelta,
    should_match: bool
) -> None:
    """Test created_* presets for correct match behavior (platform-agnostic)."""
    fpath, _ = file_and_times
    stat = fpath.stat()
    # Use mtime as the reference for 'now', but let the filter handle stat_result
    now = dt.datetime.fromtimestamp(stat.st_mtime) + offset
    preset: Filter = preset_func(now)
    result = preset.match(fpath, now=now.timestamp(), stat_result=stat)
    assert result is should_match, (
        f"Preset {preset_func.__name__} with now={now} expected {should_match} but got {result}"
    )


@pytest.mark.parametrize(
    "preset_func, offset, should_match",
    [
        (modified_this_minute, dt.timedelta(minutes=0), True),
        (modified_this_minute, dt.timedelta(minutes=1), False),
        (created_this_minute, dt.timedelta(minutes=0), True),
        (created_this_minute, dt.timedelta(minutes=1), False),
        (modified_yesterday, dt.timedelta(days=0), False),
        (modified_yesterday, dt.timedelta(days=1), True),
        (created_yesterday, dt.timedelta(days=0), False),
        (created_yesterday, dt.timedelta(days=1), True),
    ]
)
def test_new_presets(
    file_and_times: tuple[pathlib.Path, dt.datetime],
    preset_func: typing.Callable[[dt.datetime | None], Filter],
    offset: dt.timedelta,
    should_match: bool
) -> None:
    """Test new presets for minute and yesterday match behavior."""
    fpath, mtime = file_and_times
    stat = fpath.stat()
    # For minute presets, use mtime as base
    if preset_func in [modified_this_minute, created_this_minute]:
        now = mtime + offset
        preset: Filter = preset_func(now)
        result = preset.match(fpath, now=now.timestamp(), stat_result=stat)
    # For yesterday presets, shift 'now' by offset and check
    else:
        now = mtime + offset
        preset: Filter = preset_func(now)
        result = preset.match(fpath, now=now.timestamp(), stat_result=stat)
    assert result is should_match, (
        f"Preset {preset_func.__name__} with now={now} expected {should_match} but got {result}"
    )


@pytest.mark.parametrize(
    "preset_func, offset, should_match",
    [
        (created_this_minute, dt.timedelta(minutes=0), True),
        (created_this_minute, dt.timedelta(minutes=1), False),
        (created_yesterday, dt.timedelta(days=0), False),
        (created_yesterday, dt.timedelta(days=1), True),
    ]
)
def test_new_created_presets(
    file_and_times: tuple[pathlib.Path, dt.datetime],
    preset_func: typing.Callable[[dt.datetime | None], Filter],
    offset: dt.timedelta,
    should_match: bool
) -> None:
    """Test new created_* presets for minute and yesterday (platform-agnostic)."""
    fpath, _ = file_and_times
    stat = fpath.stat()
    now = dt.datetime.fromtimestamp(stat.st_mtime) + offset
    preset: Filter = preset_func(now)
    result = preset.match(fpath, now=now.timestamp(), stat_result=stat)
    assert result is should_match, (
        f"Preset {preset_func.__name__} with now={now} expected {should_match} but got {result}"
    )


@pytest.fixture
def edge_case_file(tmp_path:pathlib.Path) -> pathlib.Path:
    """Fixture for edge case file, auto-deleted after test."""
    fpath:pathlib.Path = tmp_path / "edge_case.txt"
    fpath.write_text("edge")
    mtime = dt.datetime(2025, 1, 1, 0, 0, 0)
    os.utime(fpath, (mtime.timestamp(), mtime.timestamp()))
    return fpath


@pytest.fixture
def edge_case_created_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """Fixture for edge case file for creation time, auto-deleted after test."""
    fpath: pathlib.Path = tmp_path / "edge_case_created.txt"
    fpath.write_text("edge created")
    # Creation time is set by the OS; we read it from stat
    return fpath


def make_mock_stat(modified_time: float) -> object:
    """Return a mock stat object with creation time set to modified_time."""
    stat = MagicMock()
    stat.st_mtime = modified_time
    stat.st_ctime = modified_time
    stat.st_birthtime = modified_time  # For platforms that support birthtime
    return stat


@pytest.mark.parametrize(
    "now, expected",
    [
        (dt.datetime(2024, 1, 1, 0, 0, 0), "not this year, not this month, not today, not this hour, not this minute"),
        (dt.datetime(2025, 2, 1, 0, 0, 0), "this year, not this month, not today, not this hour, not this minute"),
        (dt.datetime(2025, 1, 2, 0, 0, 0), "this year, this month, not today, not this hour, not this minute"),
        (dt.datetime(2025, 1, 1, 1, 0, 0), "this year, this month, today, not this hour, not this minute"),
        (dt.datetime(2025, 1, 1, 0, 1, 0), "this year, this month, today, this hour, not this minute"),
        (dt.datetime(2025, 1, 1, 0, 0, 1), "this year, this month, today, this hour, this minute"),
        (dt.datetime(2025, 1, 1, 0, 0, 0), "this year, this month, today, this hour, this minute"),
    ]
)
def test_modified_edge_case_param(edge_case_file: pathlib.Path, now: dt.datetime, expected: str):
    """Parametrized edge case: file modified on 2025-01-01 00:00:00, check year/month/day/hour/minute matches with assert strings."""
    fpath = edge_case_file
    stat = fpath.stat()
    results = {
        "year": modified_this_year(now).match(fpath, now=now.timestamp(), stat_result=stat),
        "month": modified_this_month(now).match(fpath, now=now.timestamp(), stat_result=stat),
        "today": modified_today(now).match(fpath, now=now.timestamp(), stat_result=stat),
        "hour": modified_this_hour(now).match(fpath, now=now.timestamp(), stat_result=stat),
        "minute": modified_this_minute(now).match(fpath, now=now.timestamp(), stat_result=stat),
    }
    assert results["year"] == ("not this year" not in expected), f"Year match failed for now={now}: expected {'not this year' not in expected}, got {results['year']}"
    assert results["month"] == ("not this month" not in expected), f"Month match failed for now={now}: expected {'not this month' not in expected}, got {results['month']}"
    assert results["today"] == ("not today" not in expected), f"Day match failed for now={now}: expected {'not today' not in expected}, got {results['today']}"
    assert results["hour"] == ("not this hour" not in expected), f"Hour match failed for now={now}: expected {'not this hour' not in expected}, got {results['hour']}"
    assert results["minute"] == ("not this minute" not in expected), f"Minute match failed for now={now}: expected {'not this minute' not in expected}, got {results['minute']}"


@pytest.mark.parametrize(
    "created_time, now, expected",
    [
        (dt.datetime(2025, 1, 1, 0, 0, 0), dt.datetime(2025, 1, 1, 0, 0, 0), True),
        (dt.datetime(2025, 1, 1, 0, 0, 0), dt.datetime(2025, 1, 2, 0, 0, 0), False),
        (dt.datetime(2025, 1, 1, 0, 0, 0), dt.datetime(2025, 2, 1, 0, 0, 0), False),
        (dt.datetime(2025, 1, 1, 0, 0, 0), dt.datetime(2026, 1, 1, 0, 0, 0), False),
    ]
)
def test_created_today_with_mock(tmp_path: pathlib.Path, created_time: dt.datetime, now: dt.datetime, expected: bool):
    """Test created_today using a mock stat object with controlled creation time."""
    fpath = tmp_path / "mockfile.txt"
    fpath.write_text("mock")
    stat = make_mock_stat(created_time.timestamp())
    preset = created_today(now)
    result = preset.match(fpath, now=now.timestamp(), stat_result=stat)
    assert result is expected, f"created_today: created={created_time}, now={now}, expected={expected}, got={result}"
