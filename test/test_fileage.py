import datetime as dt
import operator
import pathlib

from pathql.filters.date_filename import ymdh_filename
from pathql.filters.fileage import FilenameAgeDays, FilenameAgeHours, FilenameAgeYears


def make_file(date: dt.datetime, name:str="archive", ext:str="txt", date_width:str="hour"):
    """Generate a pathlib.Path with a date-encoded filename."""
    fname = ymdh_filename(name, ext, date_width=date_width, now_=date)
    return pathlib.Path(fname)




def test_filename_age_hours():
    now = dt.datetime(2025, 10, 22, 11)
    file_date = now - dt.timedelta(hours=2)
    path = make_file(file_date)
    filt = FilenameAgeHours(operator.lt, 3)
    assert filt.match(path, now=now)
    filt = FilenameAgeHours(operator.ge, 2)
    assert filt.match(path, now=now)
    filt = FilenameAgeHours(operator.eq, 2)
    assert filt.match(path, now=now)


def test_filename_age_days():
    now = dt.datetime(2025, 10, 22, 11)
    file_date = now - dt.timedelta(days=7)
    path = make_file(file_date, date_width="day")
    filt = FilenameAgeDays(operator.lt, 10)
    assert filt.match(path, now=now)
    filt = FilenameAgeDays(operator.ge, 7)
    assert filt.match(path, now=now)
    filt = FilenameAgeDays(operator.eq, 7)
    assert filt.match(path, now=now)


def test_filename_age_years():
    now = dt.datetime(2025, 1, 1, 0, 0)
    file_date = now.replace(year=2020)
    path = make_file(file_date, date_width="year")
    filt = FilenameAgeYears(operator.ge, 5)
    assert filt.match(path, now=now)  # Should be True, exactly 5 years
    filt = FilenameAgeYears(operator.ge, 6)
    assert not filt.match(path, now=now)
    filt = FilenameAgeYears(operator.eq, 5)
    assert filt.match(path, now=now)
    filt = FilenameAgeYears(operator.eq, 4)
    assert not filt.match(path, now=now)


def test_filename_age_missing_date():
    now = dt.datetime(2025, 10, 22, 11)
    path = pathlib.Path("archive.txt")
    filt = FilenameAgeDays(operator.lt, 10)
    assert not filt.match(path, now=now)


def test_filename_age_years_exact_4_years():
    """
    Test a 4-year span where the age calculation is exact.

    This works because 4 years is exactly 4 * 365.25 days = 1461 days,
    and there are no fractional leap year effects to cause rounding errors.
    """
    # Jan 1, 2021 to Jan 1, 2025 is exactly 4 years
    file_date = dt.datetime(2021, 1, 1, 0, 0)
    now = dt.datetime(2025, 1, 1, 0, 0)
    path = make_file(file_date, date_width="year")
    filt = FilenameAgeYears(operator.eq, 4)
    assert filt.match(path, now=now)
    filt = FilenameAgeYears(operator.ge, 4)
    assert filt.match(path, now=now)
    filt = FilenameAgeYears(operator.lt, 5)
    assert filt.match(path, now=now)
    filt = FilenameAgeYears(operator.gt, 4)
    assert not filt.match(path, now=now)
    filt = FilenameAgeYears(operator.eq, 5)
    assert not filt.match(path, now=now)
    assert not filt.match(path, now=now)
    assert not filt.match(path, now=now)
    assert not filt.match(path, now=now)
    assert not filt.match(path, now=now)
    assert not filt.match(path, now=now)
    assert not filt.match(path, now=now)
    assert not filt.match(path, now=now)
