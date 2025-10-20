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
    # Arrange
    fpath, mtime = file_and_times
    now: dt.datetime = mtime + offset
    stat = fpath.stat()
    preset: Filter = preset_func(now)

    # Act
    result = preset.match(fpath, now=now, stat_result=stat)

    # Assert
    assert result is should_match, (
        f"Preset {preset_func.__name__} with {now=} {mtime=} expected {should_match} but got {result}"
    )


def set_file_mtime(path: pathlib.Path, mtime: float) -> None:
    """Set the modification time of a file."""
    os.utime(path, (mtime, mtime))


@pytest.fixture(scope="module")
def file_and_times() -> typing.Generator[tuple[pathlib.Path, dt.datetime], None, None]:
    """Fixture yielding a file and its mtime for testing."""

    # Arrange
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
    # Arrange
    fpath, _ = file_and_times
    stat = fpath.stat()
    now = dt.datetime.fromtimestamp(stat.st_mtime) + offset
    preset: Filter = preset_func(now)

    # Act
    result = preset.match(fpath, now=now, stat_result=stat)

    # Assert
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
    # Arrange
    fpath, mtime = file_and_times
    stat = fpath.stat()
    now = mtime + offset
    preset: Filter = preset_func(now)

    # Act
    result = preset.match(fpath, now=now, stat_result=stat)

    # Assert
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
    # Arrange
    fpath, _ = file_and_times
    stat = fpath.stat()
    now = dt.datetime.fromtimestamp(stat.st_mtime) + offset
    preset: Filter = preset_func(now)

    # Act
    result = preset.match(fpath, now=now, stat_result=stat)

    # Assert
    assert result is should_match, (
        f"Preset {preset_func.__name__} with now={now} expected {should_match} but got {result}"
    )


@pytest.fixture
def edge_case_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """Fixture for edge case file, auto-deleted after test."""
    # Arrange
    fpath = tmp_path / "edge_case.txt"
    fpath.write_text("edge case")

    # Act
    yield fpath

    # Assert
    fpath.unlink()


@pytest.fixture
def edge_case_created_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """Fixture for edge case file for creation time, auto-deleted after test."""

    # Arrange
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
    # Arrange
    fpath = tmp_path / "mockfile.txt"
    fpath.write_text("mock")
    stat = make_mock_stat(created_time.timestamp())
    preset = created_today(now)

    # Act
    result = preset.match(fpath, now=now.timestamp(), stat_result=stat)

    # Assert
    assert result is expected, f"created_today: created={created_time}, now={now}, expected={expected}, got={result}"


def test_modified_this_year(tmp_path: pathlib.Path):
    # Arrange
    fpath = tmp_path / "testfile_year.txt"
    fpath.write_text("test")
    standard_time = dt.datetime(2025, 1, 1, 0, 0, 0)
    set_file_mtime(fpath, standard_time.timestamp())

    # Act & Assert
    assert modified_this_year(standard_time).match(fpath, now=standard_time) is True
    assert modified_this_year(standard_time - dt.timedelta(days=366)).match(fpath, now=standard_time - dt.timedelta(days=366)) is False
    assert modified_this_year(standard_time + dt.timedelta(days=366)).match(fpath, now=standard_time + dt.timedelta(days=366)) is False


def test_modified_this_month(tmp_path: pathlib.Path):
    # Arrange
    fpath = tmp_path / "testfile_month.txt"
    fpath.write_text("test")
    standard_time = dt.datetime(2025, 1, 15, 0, 0, 0)
    set_file_mtime(fpath, standard_time.timestamp())

    # Act & Assert
    assert modified_this_month(standard_time).match(fpath, now=standard_time) is True
    assert modified_this_month(standard_time - dt.timedelta(days=32)).match(fpath, now=standard_time - dt.timedelta(days=32)) is False
    assert modified_this_month(standard_time + dt.timedelta(days=32)).match(fpath, now=standard_time + dt.timedelta(days=32)) is False


def test_modified_today(tmp_path: pathlib.Path):
    # Arrange
    fpath = tmp_path / "testfile_day.txt"
    fpath.write_text("test")
    standard_time = dt.datetime(2025, 1, 1, 12, 0, 0)
    set_file_mtime(fpath, standard_time.timestamp())

    # Act & Assert
    assert modified_today(standard_time).match(fpath, now=standard_time) is True
    assert modified_today(standard_time - dt.timedelta(days=1)).match(fpath, now=standard_time - dt.timedelta(days=1)) is False
    assert modified_today(standard_time + dt.timedelta(days=1)).match(fpath, now=standard_time + dt.timedelta(days=1)) is False


def test_modified_this_hour(tmp_path: pathlib.Path):
    # Arrange
    fpath = tmp_path / "testfile_hour.txt"
    fpath.write_text("test")
    standard_time = dt.datetime(2025, 1, 1, 12, 30, 0)
    set_file_mtime(fpath, standard_time.timestamp())

    # Act & Assert
    assert modified_this_hour(standard_time).match(fpath, now=standard_time) is True
    assert modified_this_hour(standard_time - dt.timedelta(hours=1)).match(fpath, now=standard_time - dt.timedelta(hours=1)) is False
    assert modified_this_hour(standard_time + dt.timedelta(hours=1)).match(fpath, now=standard_time + dt.timedelta(hours=1)) is False


def test_modified_this_minute(tmp_path: pathlib.Path):
    # Arrange
    fpath = tmp_path / "testfile_minute.txt"
    fpath.write_text("test")
    standard_time = dt.datetime(2025, 1, 1, 12, 30, 45)
    set_file_mtime(fpath, standard_time.timestamp())

    # Act & Assert
    assert modified_this_minute(standard_time).match(fpath, now=standard_time) is True
    assert modified_this_minute(standard_time - dt.timedelta(minutes=1)).match(fpath, now=standard_time - dt.timedelta(minutes=1)) is False
    assert modified_this_minute(standard_time + dt.timedelta(minutes=1)).match(fpath, now=standard_time + dt.timedelta(minutes=1)) is False


