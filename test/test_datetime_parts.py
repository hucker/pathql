"""
Tests for datetime_parts filters: YearFilter, MonthFilter, DayFilter, HourFilter, MinuteFilter, SecondFilter.
Follows AI_CONTEXT.md conventions and AAA pattern.
"""
import datetime as dt
import pathlib
import pytest
from pathql.filters.datetime_parts import YearFilter, MonthFilter, DayFilter, HourFilter, MinuteFilter, SecondFilter

def make_file_with_mtime(tmp_path: pathlib.Path, datetime_obj: dt.datetime) -> pathlib.Path:
    """Create a file at tmp_path with a specific modification time (mtime) set to the given datetime."""
    file = tmp_path / f"f_{datetime_obj.strftime('%Y%m%d%H%M%S')}"
    file.write_text("x")
    ts = datetime_obj.timestamp()
    import os
    os.utime(str(file), (ts, ts))
    return file

@pytest.mark.parametrize("year,should_match", [
    (2025, True),
    (2024, False),
])
def test_year_filter(tmp_path: pathlib.Path, year: int, should_match: bool):
    """Test YearFilter for current year and other year."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Act
    filt = YearFilter(year)
    actual = filt.match(file)
    # Assert
    assert actual is should_match, f"YearFilter({year}) should be {should_match}"

@pytest.mark.parametrize("month,should_match", [
    (5, True),
    ("may", True),
    ("May", True),
    (6, False),
    ("jun", False),
])
def test_month_filter(tmp_path: pathlib.Path, month: int | str, should_match: bool):
    """Test MonthFilter with int and string month values."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Act
    filt = MonthFilter(month)
    actual = filt.match(file)
    # Assert
    assert actual is should_match, f"MonthFilter({month}) should be {should_match}"

@pytest.mark.parametrize("day,should_match", [
    (1, True),
    (2, False),
])
def test_day_filter(tmp_path: pathlib.Path, day: int, should_match: bool):
    """Test DayFilter for current day and other day."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Act
    filt = DayFilter(day, base=dt_)
    actual = filt.match(file)
    # Assert
    assert actual is should_match, f"DayFilter({day}) should be {should_match}"



@pytest.mark.parametrize("hour,should_match", [
    (12, True),
    (13, False),
])
def test_hour_filter(tmp_path: pathlib.Path, hour: int, should_match: bool):
    """Test HourFilter for current hour and other hour."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Act
    filt = HourFilter(hour, base=dt_)
    actual = filt.match(file)
    # Assert
    assert actual is should_match, f"HourFilter({hour}) should be {should_match}"



@pytest.mark.parametrize("minute,should_match", [
    (0, True),
    (1, False),
])
def test_minute_filter(tmp_path: pathlib.Path, minute: int, should_match: bool):
    """Test MinuteFilter for current minute and other minute."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Act
    filt = MinuteFilter(minute, base=dt_)
    actual = filt.match(file)
    # Assert
    assert actual is should_match, f"MinuteFilter({minute}) should be {should_match}"

@pytest.mark.parametrize("second,should_match", [
    (0, True),
    (1, False),
])
def test_second_filter(tmp_path: pathlib.Path, second: int, should_match: bool):
    """Test SecondFilter for current second and other second."""
    # Arrange
    dt_ = dt.datetime(2025, 5, 1, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Act
    filt = SecondFilter(second, base=dt_)
    actual = filt.match(file)
    # Assert
    assert actual is should_match, f"SecondFilter({second}) should be {should_match}"
