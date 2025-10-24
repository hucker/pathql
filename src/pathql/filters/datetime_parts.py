"""Datetime part filters for filesystem queries.

These filters match files by parts of their modification, creation, or access
timestamp. Constructors validate and normalize the `attr` once; `match()` uses
the canonical attribute name.
"""

import datetime as dt
import pathlib

from dateutil.relativedelta import relativedelta

from .alias import DatetimeOrNone
from .base import Filter

MONTH_NAME_TO_NUM: dict[str | int, int] = {
    "jan": 1,
    "january": 1,
    1: 1,
    "feb": 2,
    "february": 2,
    2: 2,
    "mar": 3,
    "march": 3,
    3: 3,
    "apr": 4,
    "april": 4,
    4: 4,
    "may": 5,
    5: 5,
    "jun": 6,
    "june": 6,
    6: 6,
    "jul": 7,
    "july": 7,
    7: 7,
    "aug": 8,
    "august": 8,
    8: 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    9: 9,
    "oct": 10,
    "october": 10,
    10: 10,
    "nov": 11,
    "november": 11,
    11: 11,
    "dec": 12,
    "december": 12,
    12: 12,
}

ATTR_MAP: dict[str, str] = {
    "modified": "st_mtime",
    "created": "st_ctime",
    "accessed": "st_atime",
    "st_mtime": "st_mtime",
    "st_ctime": "st_ctime",
    "st_atime": "st_atime",
}


def normalize_attr(attr: str) -> str:
    """Return canonical stat attribute name or raise ValueError if unknown.

    This function is public and normalizes friendly names like 'modified',
    'created', 'accessed' or raw stat attribute names like 'st_mtime'.
    """
    if attr in ATTR_MAP:
        return ATTR_MAP[attr]
    raise ValueError(
        f"Unknown stat attribute {attr!r}. Valid: {', '.join(sorted(ATTR_MAP.keys()))}"
    )


class _DatetimePartFilter(Filter):
    pass


class YearFilter(_DatetimePartFilter):
    """Filter files by year (with optional base and offset)."""

    def __init__(
        self,
        year: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """Initialize a YearFilter."""
        base = base or dt.datetime.now()
        base = base + relativedelta(years=offset)
        self.year = year
        self.month = base.month
        self.day = base.day
        self.attr = normalize_attr(attr)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: "StatProxy",  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the file's year matches the filter's year."""
        st = stat_proxy.stat()
        ts = getattr(st, self.attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return dt_obj.year == self.year


class MonthFilter(Filter):
    """Filter files by month (supports month name or number)."""

    def __init__(
        self,
        month: int | str,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """Initialize a MonthFilter."""
        base = base or dt.datetime.now()
        base = base + relativedelta(months=offset)
        self.year = base.year
        self.month = self._normalize_month(month)
        self.day = base.day
        self.attr = normalize_attr(attr)

    def _normalize_month(self, v: int | str) -> int:
        key = v.strip().lower() if isinstance(v, str) else v
        if key in MONTH_NAME_TO_NUM:
            return MONTH_NAME_TO_NUM[key]
        raise ValueError(f"Unknown month: {v}")

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: "StatProxy",  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the file's year and month match the filter."""
        st = stat_proxy.stat()
        ts = getattr(st, self.attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return dt_obj.year == self.year and dt_obj.month == self.month


class DayFilter(Filter):
    """Filter files by day of month (with base/offset)."""

    def __init__(
        self,
        day: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """Initialize a DayFilter."""
        base = base or dt.datetime.now()
        base = base + relativedelta(days=offset)
        self.year = base.year
        self.month = base.month
        self.day = day
        self.attr = normalize_attr(attr)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: "StatProxy",  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the file's year, month and day match the filter."""
        st = stat_proxy.stat()
        ts = getattr(st, self.attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return (
            dt_obj.year == self.year
            and dt_obj.month == self.month
            and dt_obj.day == self.day
        )


class HourFilter(Filter):
    """Filter files by hour (with base/offset)."""

    def __init__(
        self,
        hour: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """Initialize an HourFilter."""
        base = base or dt.datetime.now()
        base = base + relativedelta(hours=offset)
        self.year = base.year
        self.month = base.month
        self.day = base.day
        self.hour = hour
        self.attr = normalize_attr(attr)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: "StatProxy",  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the file's date/time matches this hour filter."""
        st = stat_proxy.stat()
        ts = getattr(st, self.attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return (
            dt_obj.year == self.year
            and dt_obj.month == self.month
            and dt_obj.day == self.day
            and dt_obj.hour == self.hour
        )


class MinuteFilter(Filter):
    """Filter files by minute (with base/offset)."""

    def __init__(
        self,
        minute: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """Initialize a MinuteFilter."""
        base = base or dt.datetime.now()
        base = base + relativedelta(minutes=offset)
        self.year = base.year
        self.month = base.month
        self.day = base.day
        self.hour = base.hour
        self.minute = minute
        self.attr = normalize_attr(attr)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: "StatProxy",  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the file's date/time matches this minute filter."""
        st = stat_proxy.stat()
        ts = getattr(st, self.attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return (
            dt_obj.year == self.year
            and dt_obj.month == self.month
            and dt_obj.day == self.day
            and dt_obj.hour == self.hour
            and dt_obj.minute == self.minute
        )


class SecondFilter(Filter):
    """Filter files by second (with base/offset)."""

    def __init__(
        self,
        second: int,
        base: dt.datetime | None = None,
        offset: int = 0,
        attr: str = "st_mtime",
    ):
        """Initialize a SecondFilter."""
        base = base or dt.datetime.now()
        base = base + relativedelta(seconds=offset)
        self.year = base.year
        self.month = base.month
        self.day = base.day
        self.hour = base.hour
        self.minute = base.minute
        self.second = second
        self.attr = normalize_attr(attr)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: "StatProxy",  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the file's date/time matches this second filter."""
        st = stat_proxy.stat()
        ts = getattr(st, self.attr)
        dt_obj = dt.datetime.fromtimestamp(ts)
        return (
            dt_obj.year == self.year
            and dt_obj.month == self.month
            and dt_obj.day == self.day
            and dt_obj.hour == self.hour
            and dt_obj.minute == self.minute
            and dt_obj.second == self.second
        )
