import os
import tempfile
import pathlib
import time
import datetime as dt
import pytest
from pathql.filters import Modified, Created, Year, Month, Day, Hour, Minute, Second
import datetime as dtmod


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
def test_month_lookup_eq(tmp_path, month_value, should_match):
    dt = dtmod.datetime(2022, 1, 15, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt)
    assert Modified(Month == month_value).match(file) is should_match

def test_month_lookup_isin(tmp_path):
    dt = dtmod.datetime(2022, 3, 15, 12, 0, 0)
    file = make_file_with_mtime(tmp_path, dt)
    # Should match for 3, 'mar', 'March', 'MAR', and not for others
    assert Modified(Month.isin([3, "mar", "March", "MAR"])) .match(file)
    assert not Modified(Month.isin([1, "jan", "feb"])) .match(file)


def set_file_times(path, mtime=None, ctime=None):
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    # ctime cannot be set directly on all platforms, so we only test mtime-based filters reliably

def make_file_with_mtime(tmp_path, dt):
    file = tmp_path / f"f_{dt.strftime('%Y%m%d%H%M%S')}"
    file.write_text("x")
    ts = dt.timestamp()
    set_file_times(str(file), mtime=ts)
    return file

def test_modified_year_month_day(tmp_path):
    dt = dtmod.datetime(2022, 12, 25, 15, 30, 45)
    file = make_file_with_mtime(tmp_path, dt)
    # New API
    assert Modified(Year == 2022).match(file)
    assert Modified(Month == 12).match(file)
    assert Modified(Day == 25).match(file)
    assert not Modified(Year == 2021).match(file)
    # Date object support
    assert Modified(Day == dtmod.date(2022, 12, 25)).match(file)
    assert not Modified(Day == dtmod.date(2022, 12, 24)).match(file)

def test_modified_hour_minute_second(tmp_path):
    dt = dtmod.datetime(2023, 1, 2, 3, 4, 5)
    file = make_file_with_mtime(tmp_path, dt)
    assert Modified(Hour == 3).match(file)
    assert Modified(Minute == 4).match(file)
    assert Modified(Second == 5).match(file)
    assert not Modified(Hour == 4).match(file)
    # Datetime object support
    assert Modified(Hour == dtmod.datetime(2023, 1, 2, 3)).match(file)
    assert not Modified(Hour == dtmod.datetime(2023, 1, 2, 4)).match(file)
    assert Modified(Minute == dtmod.datetime(2023, 1, 2, 3, 4)).match(file)
    assert not Modified(Minute == dtmod.datetime(2023, 1, 2, 3, 5)).match(file)
    assert Modified(Second == dtmod.datetime(2023, 1, 2, 3, 4, 5)).match(file)
    assert not Modified(Second == dtmod.datetime(2023, 1, 2, 3, 4, 6)).match(file)

def test_modified_in_operators(tmp_path):
    dt = dtmod.datetime(2024, 5, 6, 7, 8, 9)
    file = make_file_with_mtime(tmp_path, dt)
    assert Modified(Month.isin([5, 6, 7])).match(file)
    assert not Modified(Month.isin([1, 2, 3])).match(file)

# Example using the provided extractor classes

def test_modified_with_extractor_classes(tmp_path):
    dt = dtmod.datetime(2025, 10, 15, 12, 34, 56)
    file = make_file_with_mtime(tmp_path, dt)
    # Year extractor
    assert Modified(Year == 2025).match(file)
    # Month extractor
    assert Modified(Month == 10).match(file)
    # Hour in
    assert Modified(Hour.isin([12, 13])).match(file)
    # Date object for day
    assert Modified(Day == dtmod.date(2025, 10, 15)).match(file)
    # Datetime object for hour
    assert Modified(Hour == dtmod.datetime(2025, 10, 15, 12)).match(file)
    # Datetime object for minute
    assert Modified(Minute == dtmod.datetime(2025, 10, 15, 12, 34)).match(file)
    # Datetime object for second
    assert Modified(Second == dtmod.datetime(2025, 10, 15, 12, 34, 56)).match(file)

# Created filter is not reliably testable on all platforms, but we can check it runs

def test_created_runs(tmp_path):
    dt = dtmod.datetime.now()
    file = make_file_with_mtime(tmp_path, dt)
    # Should not raise
    Created(lambda d: d.year, lambda a, b: True, None).match(file)
