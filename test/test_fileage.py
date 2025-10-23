"""
Tests for FilenameAgeDays, FilenameAgeHours, and FilenameAgeYears filters.
Verifies correct age calculation and matching for files with date-encoded filenames.
"""

import datetime as dt
import operator
import pathlib
import pytest

from pathql.filters.fileage import FilenameAgeDays, FilenameAgeHours, FilenameAgeYears
from pathql.filters.date_filename import path_from_datetime


def make_file(
    date: dt.datetime, name: str = "archive", ext: str = "txt", date_width: str = "hour"
) -> pathlib.Path:
    """
    Generate a pathlib.Path with a date-encoded filename for testing.

    Args:
        date: Datetime object to encode in the filename.
        name: Archive name.
        ext: File extension.
        date_width: Date width ('year', 'month', 'day', 'hour').

    Returns:
        pathlib.Path: Path object with the encoded filename.
    """
    fname: str = path_from_datetime(name, ext, width=date_width, dt_=date)
    return pathlib.Path(fname)


@pytest.mark.parametrize(
    "filter_cls, op, threshold, file_date, now, date_width, expected",
    [
        # FilenameAgeHours tests
        (
            FilenameAgeHours,
            operator.lt,
            3,
            dt.datetime(2025, 10, 22, 9),
            dt.datetime(2025, 10, 22, 11),
            "hour",
            True,
        ),
        (
            FilenameAgeHours,
            operator.ge,
            2,
            dt.datetime(2025, 10, 22, 9),
            dt.datetime(2025, 10, 22, 11),
            "hour",
            True,
        ),
        (
            FilenameAgeHours,
            operator.eq,
            2,
            dt.datetime(2025, 10, 22, 9),
            dt.datetime(2025, 10, 22, 11),
            "hour",
            True,
        ),
        # FilenameAgeDays tests
        (
            FilenameAgeDays,
            operator.lt,
            10,
            dt.datetime(2025, 10, 15, 11),
            dt.datetime(2025, 10, 22, 11),
            "day",
            True,
        ),
        (
            FilenameAgeDays,
            operator.ge,
            7,
            dt.datetime(2025, 10, 15, 11),
            dt.datetime(2025, 10, 22, 11),
            "day",
            True,
        ),
        (
            FilenameAgeDays,
            operator.eq,
            7,
            dt.datetime(2025, 10, 15, 11),
            dt.datetime(2025, 10, 22, 11),
            "day",
            True,
        ),
        # FilenameAgeYears tests
        (
            FilenameAgeYears,
            operator.ge,
            5,
            dt.datetime(2020, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            True,
        ),
        (
            FilenameAgeYears,
            operator.ge,
            6,
            dt.datetime(2020, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            False,
        ),
        (
            FilenameAgeYears,
            operator.eq,
            5,
            dt.datetime(2020, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            True,
        ),
        (
            FilenameAgeYears,
            operator.eq,
            4,
            dt.datetime(2020, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            False,
        ),
        # Exact 4-year span
        (
            FilenameAgeYears,
            operator.eq,
            4,
            dt.datetime(2021, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            True,
        ),
        (
            FilenameAgeYears,
            operator.ge,
            4,
            dt.datetime(2021, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            True,
        ),
        (
            FilenameAgeYears,
            operator.lt,
            5,
            dt.datetime(2021, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            True,
        ),
        (
            FilenameAgeYears,
            operator.gt,
            4,
            dt.datetime(2021, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            False,
        ),
        (
            FilenameAgeYears,
            operator.eq,
            5,
            dt.datetime(2021, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 0, 0),
            "year",
            False,
        ),
        # Missing date in filename
        (
            FilenameAgeDays,
            operator.lt,
            10,
            None,
            dt.datetime(2025, 10, 22, 11),
            None,
            False,
        ),
    ],
)
def test_filename_age_filters(
    filter_cls: type,
    op: object,
    threshold: int,
    file_date: dt.datetime | None,
    now: dt.datetime,
    date_width: str | None,
    expected: bool,
) -> None:
    """
    Parameterized test for FilenameAgeDays, FilenameAgeHours, and FilenameAgeYears filters.
    Verifies correct matching for various date widths and scenarios.

    Args:
        filter_cls: The filter class to use (FilenameAgeDays, FilenameAgeHours, FilenameAgeYears).
        op: The operator for comparison.
        threshold: The threshold value for age.
        file_date: The datetime to encode in the filename (or None for missing date).
        now: The reference datetime for age calculation.
        date_width: The width of the date encoding ('year', 'month', 'day', 'hour', or None).
        expected: The expected boolean result.
    """
    # Arrange

    if file_date is not None:
        path = make_file(file_date, date_width=date_width)
    else:
        path = pathlib.Path("archive.txt")

    # Act

    filt = filter_cls(op, threshold)
    result = filt.match(path, now=now)

    # Assert

    assert result == expected
