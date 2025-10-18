"""
Tests for datetime-based filters: Modified, Created, Year, Month, Day, Hour, Minute, Second.

This module covers:
- Month lookup and normalization (numeric and string)
- Year, month, day, hour, minute, second extractors
- Operator overloading and .isin for datetime parts
- Modified and Created filter logic
"""

import os
import datetime as dt
import pytest
from pathql.filters import Modified, Created, Year, Month, Day, Hour, Minute, Second
from typing import Union
import pathlib



@pytest.mark.parametrize("month_value,should_match", [
    (1, True),
    ("jan", True),
    ("JAN", True),
    ("January", True),
    ("january", True),
    ("Feb", False),
    (2, False),
    ("Mar", False),
])
def test_month_lookup_eq(tmp_path: pathlib.Path, month_value: Union[str, int], should_match: bool):
    """
    Test Month extractor with various numeric and string values.
    Ensures Month == value works for both numbers and normalized month names.
    """
    dt_ = dt.datetime(2022, 1, 15, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    assert Modified(Month == month_value).match(file) is should_match, f"Month == {month_value} should be {should_match}"

def test_month_lookup_isin(tmp_path: pathlib.Path):
    """
    Test month lookup with isin.
    """
    dt_ = dt.datetime(2022, 3, 15, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt_)
    # Should match for 3, 'mar', 'March', 'MAR', and not for others
    assert Modified(Month.isin([3, "mar", "March", "MAR"])).match(file), "Month.isin([3, 'mar', 'March', 'MAR']) should match"
    assert not Modified(Month.isin([1, "jan", "feb"])).match(file), "Month.isin([1, 'jan', 'feb']) should not match"


def set_file_times(path: str, mtime: Union[float, None] = None):
    """
    Set the modification time (mtime) of a file. ctime is not reliably settable on all platforms.
    """
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    # ctime cannot be set directly on all platforms, so we only test mtime-based filters reliably

def make_file_with_mtime(tmp_path: pathlib.Path, datetime_obj: dt.datetime) -> pathlib.Path:
    """
    Create a file at tmp_path with a specific modification time (mtime) set to the given datetime.
    Returns the file path.
    """
    file = tmp_path / f"f_{datetime_obj.strftime('%Y%m%d%H%M%S')}"
    file.write_text("x")
    ts = datetime_obj.timestamp()
    set_file_times(str(file), mtime=ts)
    return file

def test_modified_year_month_day(tmp_path: pathlib.Path):
    """
    Test modified year, month, and day.
    """
    dt_ = dt.datetime(2022, 12, 25, 15, 30, 45)
    file = make_file_with_mtime(tmp_path, dt_)
    assert Modified(Year == 2022).match(file), "Year == 2022 should match"
    assert Modified(Month == 12).match(file), "Month == 12 should match"
    assert Modified(Day == 25).match(file), "Day == 25 should match"
    assert not Modified(Year == 2021).match(file), "Year == 2021 should not match"
    # Date object support
    assert Modified(Day == dt.date(2022, 12, 25)).match(file), "Day == date(2022, 12, 25) should match"
    assert not Modified(Day == dt.date(2022, 12, 24)).match(file), "Day == date(2022, 12, 24) should not match"

def test_modified_hour_minute_second(tmp_path: pathlib.Path):
    """
    Test modified hour, minute, and second.
    """
    dt_ = dt.datetime(2023, 1, 2, 3, 4, 5)
    file = make_file_with_mtime(tmp_path, dt_)
    assert Modified(Hour == 3).match(file), "Hour == 3 should match"
    assert Modified(Minute == 4).match(file), "Minute == 4 should match"
    assert Modified(Second == 5).match(file), "Second == 5 should match"
    assert not Modified(Hour == 4).match(file), "Hour == 4 should not match"
    # Datetime object support
    assert Modified(Hour == dt.datetime(2023, 1, 2, 3)).match(file), "Hour == datetime(2023, 1, 2, 3) should match"
    assert not Modified(Hour == dt.datetime(2023, 1, 2, 4)).match(file), "Hour == datetime(2023, 1, 2, 4) should not match"
    assert Modified(Minute == dt.datetime(2023, 1, 2, 3, 4)).match(file), "Minute == datetime(2023, 1, 2, 3, 4) should match"
    assert not Modified(Minute == dt.datetime(2023, 1, 2, 3, 5)).match(file), "Minute == datetime(2023, 1, 2, 3, 5) should not match"
    assert Modified(Second == dt.datetime(2023, 1, 2, 3, 4, 5)).match(file), "Second == datetime(2023, 1, 2, 3, 4, 5) should match"
    assert not Modified(Second == dt.datetime(2023, 1, 2, 3, 4, 6)).match(file), "Second == datetime(2023, 1, 2, 3, 4, 6) should not match"

def test_modified_in_operators(tmp_path: pathlib.Path):
    """
    Test modified in operators.
    """
    dt_ = dt.datetime(2024, 5, 6, 7, 8, 9)
    file = make_file_with_mtime(tmp_path, dt_)
    assert Modified(Month.isin([5, 6, 7])).match(file), "Month.isin([5, 6, 7]) should match"
    assert not Modified(Month.isin([1, 2, 3])).match(file), "Month.isin([1, 2, 3]) should not match"

# Example using the provided extractor classes

def test_modified_with_extractor_classes(tmp_path):
    """
    Test Modified filter with all extractor classes and various input types.
    Covers Year, Month, Day, Hour, Minute, Second with both int and datetime/date objects.
    """
    dt_ = dt.datetime(2025, 10, 15, 12, 34, 56)
    file = make_file_with_mtime(tmp_path, dt_)
    # Year extractor
    assert Modified(Year == 2025).match(file), "Year == 2025 should match"
    # Month extractor
    assert Modified(Month == 10).match(file), "Month == 10 should match"
    # Hour in
    assert Modified(Hour.isin([12, 13])).match(file), "Hour.isin([12, 13]) should match"
    # Date object for day
    assert Modified(Day == dt.date(2025, 10, 15)).match(file), "Day == date(2025, 10, 15) should match"
    # Datetime object for hour
    assert Modified(Hour == dt.datetime(2025, 10, 15, 12)).match(file), "Hour == datetime(2025, 10, 15, 12) should match"
    # Datetime object for minute
    assert Modified(Minute == dt.datetime(2025, 10, 15, 12, 34)).match(file), "Minute == datetime(2025, 10, 15, 12, 34) should match"
    # Datetime object for second
    assert Modified(Second == dt.datetime(2025, 10, 15, 12, 34, 56)).match(file), "Second == datetime(2025, 10, 15, 12, 34, 56) should match"

# Created filter is not reliably testable on all platforms, but we can check it runs
