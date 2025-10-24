"""Tests for datetime part filters (Year/Month/Day/Hour/Minute/Second)."""

import datetime as dt
import os
import pathlib
from typing import Type

import pytest

from pathql.filters.base import Filter
from pathql.filters.datetime_parts import (
    DayFilter,
    HourFilter,
    MinuteFilter,
    MonthFilter,
    SecondFilter,
    YearFilter,
)
from pathql.filters.stat_proxy import StatProxy


def get_stat_proxy(path):
    return StatProxy(path)


def make_file_with_mtime(
    tmp_path: pathlib.Path, datetime_obj: dt.datetime
) -> pathlib.Path:
    """Create file at tmp_path with a modification time (mtime) set to the given datetime."""
    file = tmp_path / f"f_{datetime_obj.strftime('%Y%m%d%H%M%S')}"
    file.write_text("x")
    ts = datetime_obj.timestamp()
    os.utime(str(file), (ts, ts))
    return file


@pytest.mark.parametrize(
    "year,should_match",
    [
        (2025, True),
        (2024, False),
    ],
)
def test_year_filter(
    tmp_path: pathlib.Path,
    year: int,
    should_match: bool,
) -> None:
    """YearFilter returns expected matches for given years."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)

    # Act
    filter_ = YearFilter(year)
    actual = filter_.match(file, get_stat_proxy(file))

    # Assert
    assert actual is should_match, f"YearFilter({year}) should be {should_match}"


@pytest.mark.parametrize(
    "month,should_match",
    [
        (5, True),
        ("may", True),
        ("May", True),
        (6, False),
        ("jun", False),
    ],
)
def test_month_filter(
    tmp_path: pathlib.Path,
    month: int | str,
    should_match: bool,
) -> None:
    """MonthFilter matches numeric and string month names."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)

    # Act
    filter_ = MonthFilter(month)
    actual = filter_.match(file, get_stat_proxy(file))

    # Assert
    assert actual is should_match, f"MonthFilter({month}) should be {should_match}"


@pytest.mark.parametrize(
    "day,should_match",
    [
        (1, True),
        (2, False),
    ],
)
def test_day_filter(
    tmp_path: pathlib.Path,
    day: int,
    should_match: bool,
) -> None:
    """DayFilter matches the expected day of month."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)

    # Act
    filter_ = DayFilter(day, base=dt_)
    actual = filter_.match(file, get_stat_proxy(file))

    # Assert
    assert actual is should_match, f"DayFilter({day}) should be {should_match}"


@pytest.mark.parametrize(
    "hour,should_match",
    [
        (12, True),
        (13, False),
    ],
)
def test_hour_filter(
    tmp_path: pathlib.Path,
    hour: int,
    should_match: bool,
) -> None:
    """HourFilter matches the expected hour of day."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)

    # Act
    filter_ = HourFilter(hour, base=dt_)
    actual = filter_.match(file, get_stat_proxy(file))

    # Assert
    assert actual is should_match, f"HourFilter({hour}) should be {should_match}"


@pytest.mark.parametrize(
    "minute,should_match",
    [
        (0, True),
        (1, False),
    ],
)
def test_minute_filter(
    tmp_path: pathlib.Path,
    minute: int,
    should_match: bool,
) -> None:
    """MinuteFilter matches the expected minute of hour."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Act
    filter_ = MinuteFilter(minute, base=dt_)
    actual = filter_.match(file, get_stat_proxy(file))
    # Assert
    assert actual is should_match, f"MinuteFilter({minute}) should be {should_match}"


@pytest.mark.parametrize(
    "second,should_match",
    [
        (0, True),
        (1, False),
    ],
)
def test_second_filter(
    tmp_path: pathlib.Path,
    second: int,
    should_match: bool,
) -> None:
    """SecondFilter matches the expected second of minute."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Act
    filter_ = SecondFilter(second, base=dt_)
    actual = filter_.match(file, get_stat_proxy(file))
    # Assert
    assert actual is should_match, f"SecondFilter({second}) should be {should_match}"


@pytest.mark.parametrize(
    "cls", [YearFilter, MonthFilter, DayFilter, HourFilter, MinuteFilter, SecondFilter]
)
def test_filters_raise_on_invalid_attr(cls: Type[Filter]) -> None:
    """All datetime part filters raise ValueError for unknown attrs."""
    # Arrange
    invalid_attr = "access_time"
    # Act / Assert - construction should fail fast with ValueError
    with pytest.raises(ValueError):
        # For simplicity, pass a minimal valid value for the constructor
        if cls is YearFilter:
            cls(2025, attr=invalid_attr)
        elif cls is MonthFilter:
            cls(1, attr=invalid_attr)
        elif cls is DayFilter:
            cls(1, attr=invalid_attr)
        elif cls is HourFilter:
            cls(0, attr=invalid_attr)
        elif cls is MinuteFilter:
            cls(0, attr=invalid_attr)
        elif cls is SecondFilter:
            cls(0, attr=invalid_attr)
        elif cls is SecondFilter:
            cls(0, attr=invalid_attr)
