import datetime
import pathlib
import pytest
from pathql.filters.date_filename import (
    y_filename,
    ym_filename,
    ymdh_filename,
    extract_date_filename_parts,
    DateFilenameParts,
)

def test_y_filename_default_year():
    now = datetime.datetime(2022, 5, 6)
    fname = y_filename("archive", "zip", now_=now)
    assert fname == "2022-archive.zip"

def test_y_filename_explicit_year():
    fname = y_filename("archive", "zip", year=2020)
    assert fname == "2020-archive.zip"

def test_ym_filename_default_year_month():
    now = datetime.datetime(2023, 7, 1)
    fname = ym_filename("backup", "tar", now_=now)
    assert fname == "2023-07_backup.tar"

def test_ym_filename_explicit_year():
    now = datetime.datetime(2024, 2, 15)
    fname = ym_filename("data", "csv", year=2024, now_=now)
    assert fname == "2024-02_data.csv"

@pytest.mark.parametrize(
    "date_width,expected",
    [
        ("year", "2025-archive.txt"),
        ("month", "2025-10_archive.txt"),
        ("day", "2025-10-22_archive.txt"),
        ("hour", "2025-10-22_11_archive.txt"),
    ]
)
def test_ymdh_filename_all_widths(date_width, expected):
    now = datetime.datetime(2025, 10, 22, 11, 8, 45)
    fname = ymdh_filename("archive", "txt", date_width=date_width, now_=now)
    assert fname == expected

def test_ymdh_filename_no_extension():
    now = datetime.datetime(2025, 10, 22, 11)
    fname = ymdh_filename("archive", "", date_width="hour", now_=now)
    assert fname == "2025-10-22_11_archive"

def test_ymdh_filename_dot_extension():
    now = datetime.datetime(2025, 10, 22, 11)
    fname = ymdh_filename("archive", ".log", date_width="hour", now_=now)
    assert fname == "2025-10-22_11_archive.log"

def test_ymdh_filename_invalid_datewidth():
    with pytest.raises(ValueError):
        ymdh_filename("archive", "txt", date_width="minute")

def test_ymdh_filename_missing_hour_manual():
    # Should raise because hour is missing for manual date_width="hour"
    with pytest.raises(ValueError):
        ymdh_filename("archive", "txt", date_width="hour", year=2025, month=10, day=22)

def test_ymdh_filename_conflicting_now_and_manual():
    # Should raise because now_ and manual date parts are both provided
    now = datetime.datetime(2025, 10, 22, 11)
    with pytest.raises(ValueError):
        ymdh_filename("archive", "txt", date_width="hour", year=2025, now_=now)

def test_ymdh_filename_manual_all_parts():
    fname = ymdh_filename("archive", "txt", date_width="hour", year=2025, month=10, day=22, hour=11)
    assert fname == "2025-10-22_11_archive.txt"

def test_extract_date_filename_parts_year():
    parts = extract_date_filename_parts("2022-archive.zip")
    assert parts == DateFilenameParts(year=2022)

def test_extract_date_filename_parts_year_month():
    parts = extract_date_filename_parts("2022-07_archive.zip")
    assert parts == DateFilenameParts(year=2022, month=7)

def test_extract_date_filename_parts_year_month_day():
    parts = extract_date_filename_parts("2022-07-15_archive.zip")
    assert parts == DateFilenameParts(year=2022, month=7, day=15)

def test_extract_date_filename_parts_year_month_day_hour():
    parts = extract_date_filename_parts("2022-07-15_13_archive.zip")
    assert parts == DateFilenameParts(year=2022, month=7, day=15, hour=13)

def test_extract_date_filename_parts_pathlib():
    path = pathlib.Path("2022-07-15_13_archive.zip")
    parts = extract_date_filename_parts(path)
    assert parts == DateFilenameParts(year=2022, month=7, day=15, hour=13)

def test_extract_date_filename_parts_missing():
    parts = extract_date_filename_parts("archive.zip")
    assert parts == DateFilenameParts()