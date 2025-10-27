import pathlib
import datetime as dt
import pytest
from pathql.filters.file_age import FilenameAgeMinutes, FilenameAgeHours, FilenameAgeDays, FilenameAgeYears
from pathql.filters.base import Filter

@pytest.mark.parametrize(
    "filter_cls, filename, unit_seconds, assert_message",
    [
        # Minutes and hours: with _ and archive string
        (FilenameAgeMinutes, "2019-01-01_00_foo.txt", 60.0, "Minutes filter, _ separator, archive"),
        (FilenameAgeHours, "2019-01-01_00-bar.txt", 3600.0, "Hours filter, _ separator, archive with dash"),
        (FilenameAgeMinutes, "2019-01-01_00.txt", 60.0, "Minutes filter, _ separator, no archive"),
        (FilenameAgeHours, "2019-01-01_00.txt", 3600.0, "Hours filter, _ separator, no archive"),
        # Days: with - and archive string
        (FilenameAgeDays, "2019-01-01_foo.txt", 86400.0, "Days filter, _ separator, archive"),
        (FilenameAgeDays, "2019-01-01-bar.txt", 86400.0, "Days filter, - separator, archive"),
        (FilenameAgeDays, "2019-01-01.txt", 86400.0, "Days filter, no archive"),
        # Years: with archive string
        (FilenameAgeYears, "2019_foo.txt", 86400.0 * 365, "Years filter, _ separator, archive"),
        (FilenameAgeYears, "2019-bar.txt", 86400.0 * 365, "Years filter, - separator, archive"),
        (FilenameAgeYears, "2019.txt", 86400.0 * 365, "Years filter, no archive"),
    ]
)
@pytest.mark.parametrize("path_type", [str, pathlib.Path])  # Test both str and Path types for filename input
def test_fileage_operators(filter_cls: type[Filter], filename: str, unit_seconds: float, assert_message: str, path_type):
    # Arrange
    file_date = dt.datetime(2019, 1, 1, 0, 0)
    now = dt.datetime(2019, 1, 2, 0, 0)  # 1 day later
    path = path_type(filename)
    age_units = int((now - file_date).total_seconds() // unit_seconds)

    # Act & Assert
    # < operator
    assert (filter_cls() < (age_units + 1)).match(path, now=now) is True, f"{assert_message}: < operator, age={age_units}"
    assert (filter_cls() < age_units).match(path, now=now) is False, f"{assert_message}: < operator, age={age_units}"

    # <= operator
    assert (filter_cls() <= age_units).match(path, now=now) is True, f"{assert_message}: <= operator, age={age_units}"
    assert (filter_cls() <= (age_units - 1)).match(path, now=now) is False, f"{assert_message}: <= operator, age={age_units}"

    # > operator
    assert (filter_cls() > (age_units - 1)).match(path, now=now) is True, f"{assert_message}: > operator, age={age_units}"
    assert (filter_cls() > age_units).match(path, now=now) is False, f"{assert_message}: > operator, age={age_units}"

    # >= operator
    assert (filter_cls() >= age_units).match(path, now=now) is True, f"{assert_message}: >= operator, age={age_units}"
    assert (filter_cls() >= (age_units + 1)).match(path, now=now) is False, f"{assert_message}: >= operator, age={age_units}"

    # == operator
    assert (filter_cls() == age_units).match(path, now=now) is True, f"{assert_message}: == operator, age={age_units}"
    assert (filter_cls() == (age_units + 1)).match(path, now=now) is False, f"{assert_message}: == operator, age={age_units}"

    # != operator
    assert (filter_cls() != (age_units + 1)).match(path, now=now) is True, f"{assert_message}: != operator, age={age_units}"
    assert (filter_cls() != age_units).match(path, now=now) is False, f"{assert_message}: != operator, age={age_units}"