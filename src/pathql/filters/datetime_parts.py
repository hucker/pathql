"""
Datetime part filters for filesystem queries.

These filters allow you to match files based on specific parts of their modification,
creation, or access datetime. Each filter (YearFilter, MonthFilter, DayFilter, HourFilter,
MinuteFilter, SecondFilter) matches files whose stat timestamp matches the specified part(s).

Usage:
    - YearFilter(year, base=None, offset=0, attr="modified")
    - MonthFilter(month, base=None, offset=0, attr="created")
    - DayFilter(day, base=None, offset=0, attr="accessed")
    - ...

Arguments:
    - value (int or str): The part to match (e.g., year=2025, month="may" or 5, day=16, etc.)
    - base (datetime, optional): Reference datetime for offset calculation. Defaults to now.
    - offset (int, optional): Offset to apply to the base datetime (e.g., offset=1 for next year/month/day).
    - attr (str, optional): Which stat attribute to use. Accepts "modified", "created", "accessed" or
      "st_mtime", "st_ctime", "st_atime".

Matching logic:
    - The filter extracts the relevant part(s) from the file's stat timestamp (using the specified attr).
    - It compares the extracted part(s) to the filter's value(s).
    - For MonthFilter, both string names ("may", "january") and integers (1-12) are supported.
    - For DayFilter, HourFilter, MinuteFilter, SecondFilter, the filter matches only if all parts
      (year, month, day, etc.) match exactly.

Examples:
    YearFilter(2025)           # Matches files modified in 2025
    MonthFilter("may")        # Matches files modified in May of the base year
    DayFilter(16, base=dt.datetime(2025, 10, 16))
        # Matches files modified on Oct 16, 2025
    HourFilter(12)            # Matches files modified at 12:00 of the base day
    MinuteFilter(30)          # Matches files modified at minute 30 of the base hour
    SecondFilter(0)           # Matches files modified at second 0 of the base minute

Stat attribute mapping:
    - "modified" -> st_mtime
    - "created"  -> st_ctime
    - "accessed" -> st_atime
    - You can also use the raw stat attribute names directly.

See README.md for more usage examples.
"""
import datetime as dt
import pathlib
from dateutil.relativedelta import relativedelta
from .base import Filter
from .alias import DatetimeOrNone, StatResultOrNone

MONTH_NAME_TO_NUM: dict[str | int, int] = {
    "jan": 1, "january": 1, 1:1,
    "feb": 2, "february": 2, 2:2,
    "mar": 3, "march": 3, 3:3,
    "apr": 4, "april": 4, 4:4,
    "may": 5, 5:5,
    "jun": 6, "june": 6, 6:6,
    "jul": 7, "july": 7, 7:7,
    "aug": 8, "august": 8, 8:8,
    "sep": 9, "sept": 9, "september": 9, 9:9,
    "oct": 10, "october": 10, 10:10,
    "nov": 11, "november": 11, 11:11,
    "dec": 12, "december": 12, 12:12,

}

ATTR_MAP: dict[str, str] = {
    "modified": "st_mtime",
    "created": "st_ctime",
    "accessed": "st_atime",
    "st_mtime": "st_mtime",
    "st_ctime": "st_ctime",
    "st_atime": "st_atime",
}


class YearFilter(Filter):
    """Filter for year, with base, offset, and attr."""
    def __init__(
        self,
        year: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """
        Initialize a YearFilter.
        Args:
            year: Year to match.
            base: Reference datetime for offset calculation (default: now).
            offset: Years to offset from base.
            attr: Stat attribute to use (default: "st_mtime").
        """
        base = base or dt.datetime.now()
        base = base + relativedelta(years=offset)
        self.year = year
        self.month = base.month
        self.day = base.day
        self.attr = attr
    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """
        Return True if the file's year matches the filter's year.
        Args:
            path: Path to file.
            now: Optional override for current datetime.
            stat_result: Optional override for stat result.
        """
        stat_result = stat_result or path.stat()
        attr = ATTR_MAP.get(self.attr, self.attr)
        ts = getattr(stat_result, attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return dt_obj.year == self.year

class MonthFilter(Filter):
    """Filter for month, with base, offset, flexible names, and attr."""
    def __init__(
        self,
        month: int | str,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """
        Initialize a MonthFilter.
        Args:
            month: Month to match (int or str).
            base: Reference datetime for offset calculation (default: now).
            offset: Months to offset from base.
            attr: Stat attribute to use (default: "st_mtime").
        """
        base = base or dt.datetime.now()
        base = base + relativedelta(months=offset)
        self.year = base.year
        self.month = self._normalize_month(month)
        self.day = base.day
        self.attr = attr
    def _normalize_month(
        self,
        v: int | str,
    ) -> int:
        """
        Normalize month input to integer (supports names and numbers).
        Args:
            v: Month as int or str.
        Returns:
            int: Month number (1-12).
        """
        key = v.strip().lower() if isinstance(v, str) else v
        if key in MONTH_NAME_TO_NUM:
            return MONTH_NAME_TO_NUM[key]
        raise ValueError(f"Unknown month: {v}")
    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """
        Return True if the file's year and month match the filter's year and month.
        Args:
            path: Path to file.
            now: Optional override for current datetime.
            stat_result: Optional override for stat result.
        """
        stat_result = stat_result or path.stat()
        attr = ATTR_MAP.get(self.attr, self.attr)
        ts = getattr(stat_result, attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return dt_obj.year == self.year and dt_obj.month == self.month

class DayFilter(Filter):
    """Filter for day, with base, offset, and attr."""
    def __init__(
        self,
        day: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """
        Initialize a DayFilter.
        Args:
            day: Day to match.
            base: Reference datetime for offset calculation (default: now).
            offset: Days to offset from base.
            attr: Stat attribute to use (default: "st_mtime").
        """
        base = base or dt.datetime.now()
        base = base + relativedelta(days=offset)
        self.year = base.year
        self.month = base.month
        self.day = day
        self.attr = attr
    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """
        Return True if the file's year, month, and day match the filter's values.
        Args:
            path: Path to file.
            now: Optional override for current datetime.
            stat_result: Optional override for stat result.
        """
        stat_result = stat_result or path.stat()
        attr = ATTR_MAP.get(self.attr, self.attr)
        ts = getattr(stat_result, attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return dt_obj.year == self.year and dt_obj.month == self.month and dt_obj.day == self.day

class HourFilter(Filter):
    """Filter for hour, with base, offset, and attr."""
    def __init__(
        self,
        hour: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """
        Initialize an HourFilter.
        Args:
            hour: Hour to match.
            base: Reference datetime for offset calculation (default: now).
            offset: Hours to offset from base.
            attr: Stat attribute to use (default: "st_mtime").
        """
        base = base or dt.datetime.now()
        base = base + relativedelta(hours=offset)
        self.year = base.year
        self.month = base.month
        self.day = base.day
        self.hour = hour
        self.attr = attr
    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """
        Return True if the file's year, month, day, and hour match the filter's values.
        Args:
            path: Path to file.
            now: Optional override for current datetime.
            stat_result: Optional override for stat result.
        """
        stat_result = stat_result or path.stat()
        attr = ATTR_MAP.get(self.attr, self.attr)
        ts = getattr(stat_result, attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return (dt_obj.year == self.year and dt_obj.month == self.month and dt_obj.day == self.day and dt_obj.hour == self.hour)

class MinuteFilter(Filter):
    """Filter for minute, with base, offset, and attr."""
    def __init__(
        self,
        minute: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """
        Initialize a MinuteFilter.
        Args:
            minute: Minute to match.
            base: Reference datetime for offset calculation (default: now).
            offset: Minutes to offset from base.
            attr: Stat attribute to use (default: "st_mtime").
        """
        base = base or dt.datetime.now()
        base = base + relativedelta(minutes=offset)
        self.year = base.year
        self.month = base.month
        self.day = base.day
        self.hour = base.hour
        self.minute = minute
        self.attr = attr
    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """
        Return True if the file's year, month, day, hour, and minute match the filter's values.
        Args:
            path: Path to file.
            now: Optional override for current datetime.
            stat_result: Optional override for stat result.
        """
        stat_result = stat_result or path.stat()
        attr = ATTR_MAP.get(self.attr, self.attr)
        ts = getattr(stat_result, attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return (dt_obj.year == self.year and dt_obj.month == self.month and dt_obj.day == self.day and dt_obj.hour == self.hour and dt_obj.minute == self.minute)

class SecondFilter(Filter):
    """Filter for second, with base, offset, and attr."""
    def __init__(
        self,
        second: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """
        Initialize a SecondFilter.
        Args:
            second: Second to match.
            base: Reference datetime for offset calculation (default: now).
            offset: Seconds to offset from base.
            attr: Stat attribute to use (default: "st_mtime").
        """
        base = base or dt.datetime.now()
        base = base + relativedelta(seconds=offset)
        self.year = base.year
        self.month = base.month
        self.day = base.day
        self.hour = base.hour
        self.minute = base.minute
        self.second = second
        self.attr = attr
    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """
        Return True if the file's year, month, day, hour, minute, and second match the filter's values.
        Args:
            path: Path to file.
            now: Optional override for current datetime.
            stat_result: Optional override for stat result.
        """
        stat_result = stat_result or path.stat()
        attr = ATTR_MAP.get(self.attr, self.attr)
        ts = getattr(stat_result, attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return (dt_obj.year == self.year and dt_obj.month == self.month and dt_obj.day == self.day and dt_obj.hour == self.hour and dt_obj.minute == self.minute and dt_obj.second == self.second)
