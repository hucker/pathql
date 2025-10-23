"""Tests for date_filename.py utilities."""

import datetime as dt
import pathlib
from typing import Any, Callable

import pytest

from pathql.filters.date_filename import (
    DateFilenameParts,
    filename_to_datetime_parts,
    filename_to_datetime,
    path_from_datetime,
    path_from_dt_ints,
)


@pytest.mark.parametrize(
    "filename,expected,assert_message",
    [
        ("2022-archive.zip", DateFilenameParts(year=2022), "Y only, archive/ext"),
        ("2022-archive", DateFilenameParts(year=2022), "Y only, archive/no ext"),
        ("2022-", DateFilenameParts(year=2022), "Y only, no archive/ext"),
        (
            "2022-07_archive.zip",
            DateFilenameParts(year=2022, month=7),
            "YM, archive/ext",
        ),
        (
            "2022-07_archive",
            DateFilenameParts(year=2022, month=7),
            "YM, archive/no ext",
        ),
        ("2022-07_", DateFilenameParts(year=2022, month=7), "YM, no archive/ext"),
        (
            "2022-07-15_archive.zip",
            DateFilenameParts(year=2022, month=7, day=15),
            "YMD, archive/ext",
        ),
        (
            "2022-07-15_archive",
            DateFilenameParts(year=2022, month=7, day=15),
            "YMD, archive/no ext",
        ),
        (
            "2022-07-15_",
            DateFilenameParts(year=2022, month=7, day=15),
            "YMD, no archive/ext",
        ),
        (
            "2022-07-15_13_archive.zip",
            DateFilenameParts(year=2022, month=7, day=15, hour=13),
            "YMDH, archive/ext",
        ),
        (
            "2022-07-15_13_archive",
            DateFilenameParts(year=2022, month=7, day=15, hour=13),
            "YMDH, archive/no ext",
        ),
        (
            "2022-07-15_13_",
            DateFilenameParts(year=2022, month=7, day=15, hour=13),
            "YMDH, no archive/ext",
        ),
        (
            pathlib.Path("2022-07-15_13_archive.zip"),
            DateFilenameParts(year=2022, month=7, day=15, hour=13),
            "YMDH, Path obj",
        ),
    ],
)
def test_filename_to_datetime_parts_all_formats(filename, expected, assert_message):
    # Arrange & Act
    parts = filename_to_datetime_parts(filename)
    # Assert
    assert parts == expected, assert_message


@pytest.mark.parametrize(
    "filename,expected,assert_message",
    [
        ("2022-archive.zip", dt.datetime(2022, 1, 1, 0, 0, 0), "Y only, archive/ext"),
        ("2022-archive", dt.datetime(2022, 1, 1, 0, 0, 0), "Y only, archive/no ext"),
        ("2022-", dt.datetime(2022, 1, 1, 0, 0, 0), "Y only, no archive/ext"),
        ("2022-07_archive.zip", dt.datetime(2022, 7, 1, 0, 0, 0), "YM, archive/ext"),
        ("2022-07_archive", dt.datetime(2022, 7, 1, 0, 0, 0), "YM, archive/no ext"),
        ("2022-07_", dt.datetime(2022, 7, 1, 0, 0, 0), "YM, no archive/ext"),
        (
            "2022-07-15_archive.zip",
            dt.datetime(2022, 7, 15, 0, 0, 0),
            "YMD, archive/ext",
        ),
        (
            "2022-07-15_archive",
            dt.datetime(2022, 7, 15, 0, 0, 0),
            "YMD, archive/no ext",
        ),
        ("2022-07-15_", dt.datetime(2022, 7, 15, 0, 0, 0), "YMD, no archive/ext"),
        (
            "2022-07-15_13_archive.zip",
            dt.datetime(2022, 7, 15, 13, 0, 0),
            "YMDH, archive/ext",
        ),
        (
            "2022-07-15_13_archive",
            dt.datetime(2022, 7, 15, 13, 0, 0),
            "YMDH, archive/no ext",
        ),
        ("2022-07-15_13_", dt.datetime(2022, 7, 15, 13, 0, 0), "YMDH, no archive/ext"),
        (
            pathlib.Path("2022-07-15_13_archive.zip"),
            dt.datetime(2022, 7, 15, 13, 0, 0),
            "YMDH, Path obj",
        ),
    ],
)
def test_filename_to_datetime_all_formats(
    filename: str, expected: dt.datetime, assert_message: str
):
    # Arrange: filename and expected datetime
    # Act: convert filename to datetime
    dt = filename_to_datetime(filename)
    # Assert: check result matches expectation
    assert dt == expected, assert_message


@pytest.mark.parametrize(
    "filename,assert_message",
    [
        ("archive.zip", "no date, archive/ext"),
        ("not_a_date_archive.txt", "not a date, archive/ext"),
        ("", "empty string"),
        ("archive", "no date, archive/no ext"),
        ("_archive.zip", "no date, just separator"),
        ("-", "no date, just separator"),
    ],
)
def test_filename_to_datetime_invalid_cases(filename: str, assert_message: str):
    # Arrange: filename
    # Act & Assert: should raise ValueError for missing year
    with pytest.raises(ValueError, match="Year is required"):
        filename_to_datetime(filename)

@pytest.mark.parametrize(
    "args,expected,assert_message",
    [
        # path_from_dt_ints tests
        (
            {"name": "archive", "ext": "zip", "year": 2022},
            "2022-archive.zip",
            "year only",
        ),
        (
            {"name": "archive", "ext": "", "year": 2022},
            "2022-archive",
            "year only, no ext",
        ),
        (
            {"name": "archive", "ext": ".log", "year": 2022},
            "2022-archive.log",
            "year only, dot ext",
        ),
        (
            {"name": "backup", "ext": "tar", "year": 2023, "month": 7},
            "2023-07_backup.tar",
            "year/month",
        ),
        (
            {"name": "backup", "ext": "", "year": 2023, "month": 7},
            "2023-07_backup",
            "year/month, no ext",
        ),
        (
            {"name": "backup", "ext": ".log", "year": 2023, "month": 7},
            "2023-07_backup.log",
            "year/month, dot ext",
        ),
        (
            {"name": "report", "ext": "csv", "year": 2022, "month": 8, "day": 5},
            "2022-08-05_report.csv",
            "year/month/day",
        ),
        (
            {"name": "report", "ext": "", "year": 2022, "month": 8, "day": 5},
            "2022-08-05_report",
            "year/month/day, no ext",
        ),
        (
            {"name": "report", "ext": ".log", "year": 2022, "month": 8, "day": 5},
            "2022-08-05_report.log",
            "year/month/day, dot ext",
        ),
        (
            {
                "name": "archive",
                "ext": "txt",
                "year": 2025,
                "month": 10,
                "day": 22,
                "hour": 11,
            },
            "2025-10-22_11_archive.txt",
            "year/month/day/hour",
        ),
        (
            {
                "name": "archive",
                "ext": "",
                "year": 2025,
                "month": 10,
                "day": 22,
                "hour": 11,
            },
            "2025-10-22_11_archive",
            "year/month/day/hour, no ext",
        ),
        (
            {
                "name": "archive",
                "ext": ".log",
                "year": 2025,
                "month": 10,
                "day": 22,
                "hour": 11,
            },
            "2025-10-22_11_archive.log",
            "year/month/day/hour, dot ext",
        ),
    ],
)
def test_path_from_dt_ints(args:dict[str,str|int], expected:str, assert_message:str):
    """
    Parameterized test for path_from_dt_ints.
    Verifies output for various combinations of date parts, extension, and archive name.
    """
    result = path_from_dt_ints(**args)
    assert result == expected, assert_message


@pytest.mark.parametrize(
    "args,expected,assert_message",
    [
        # path_from_datetime tests
        (
            {
                "name": "archive",
                "ext": "zip",
                "width": "year",
                "dt_": dt.datetime(2022, 5, 6),
            },
            "2022-archive.zip",
            "year only",
        ),
        (
            {
                "name": "backup",
                "ext": "tar",
                "width": "month",
                "dt_": dt.datetime(2023, 7, 1),
            },
            "2023-07_backup.tar",
            "year/month",
        ),
        (
            {
                "name": "report",
                "ext": "csv",
                "width": "day",
                "dt_": dt.datetime(2022, 8, 5),
            },
            "2022-08-05_report.csv",
            "year/month/day",
        ),
        (
            {
                "name": "archive",
                "ext": "txt",
                "width": "hour",
                "dt_": dt.datetime(2025, 10, 22, 11),
            },
            "2025-10-22_11_archive.txt",
            "year/month/day/hour",
        ),
        (
            {
                "name": "archive",
                "ext": "",
                "width": "hour",
                "dt_": dt.datetime(2025, 10, 22, 11),
            },
            "2025-10-22_11_archive",
            "year/month/day/hour, no ext",
        ),
        (
            {
                "name": "archive",
                "ext": ".log",
                "width": "hour",
                "dt_": dt.datetime(2025, 10, 22, 11),
            },
            "2025-10-22_11_archive.log",
            "year/month/day/hour, dot ext",
        ),
    ],
)
def test_path_from_datetime(
    args: dict[str, str | dt.datetime], expected: dt.datetime, assert_message: str
):
    """
    Parameterized test for path_from_datetime.
    Verifies output for various combinations of datetime, extension, and archive name.
    """
    result = path_from_datetime(**args)
    assert result == expected, assert_message


@pytest.mark.parametrize(
    "args,expected_exception,assert_message",
    [
        # path_from_dt_ints invalid cases
        # Removed: {"name": "archive", "ext": "zip", "year": None}, ValueError, "year is required"
        ({"name": "archive", "ext": "zip", "year": 2022, "month": None, "day": 5}, ValueError, "Invalid date string"),
        ({"name": "archive", "ext": "zip", "year": 2022, "month": 7, "day": None, "hour": 11}, ValueError, "Invalid date string"),
        # path_from_datetime invalid cases
        ({"name": "archive", "ext": "zip", "width": "decade", "dt_": dt.datetime(2022, 5, 6)}, ValueError, "Unhandled width"),
    ]
)
def test_path_from_dt_ints_and_datetime_exceptions(args: dict[str, str | dt.datetime], expected_exception: Exception, assert_message: str):
    """
    Parameterized test for path_from_dt_ints and path_from_datetime exception cases.
    """
    if "width" in args:
        func = path_from_datetime
    else:
        func = path_from_dt_ints
    with pytest.raises(expected_exception, match=assert_message):
        func(**args)
