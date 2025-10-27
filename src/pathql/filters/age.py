"""
Provides filter classes for querying files based on their age (time since last
modification) in minutes, hours, days, or years. These filters support declarative
operator overloads, allowing expressive queries such as `AgeDays < 10` or
`AgeYears >= 1`.

Classes:
    AgeMinutes  -- Filter for file age in minutes.
    AgeHours    -- Filter for file age in hours.
    AgeDays     -- Filter for file age in days.
    AgeYears    -- Filter for file age in years.

Each filter uses a comparison operator and a threshold value, and can be used to
match files whose modification time meets the specified age criteria.

NOTE: We specifically use modification time (mtime) for age calculations, as it is
widely supported across different operating systems and file systems. Creation time
(ctime) is not consistently available or consistent across platforms (surprisingly),
so we avoid using it for age-based filters. If you must have creation time-based
filtering you can build one using something like:

Created < some_datetime

This will use the created timestamp and will often be correct, surprisingly working
better on Windows than on Unix-like systems.
"""

import operator
import pathlib
from typing import Any, Callable

from .alias import StatProxyOrNone
from .attribute_filter import AttributeFilter
from .datetime_parts import normalize_attr


class AgeBase(AttributeFilter):
    def __init__(
        self,
        op: Callable[[int, int], bool] = operator.lt,
        value: int | None = None,
        *,
        attr: str = "modified",
    ) -> None:
        self.unit_seconds = getattr(self, "unit_seconds", 1.0)
        self.attr = attr
        self._stat_field = normalize_attr(attr)

        def extractor(
            path: pathlib.Path, stat_proxy: StatProxyOrNone, now: Any = None
        ) -> int:
            if stat_proxy is None:
                raise ValueError("stat_proxy required for age extraction")
            import datetime

            if now is None:
                now = datetime.datetime.now()
            st = stat_proxy.stat()
            mtime_ts = getattr(st, self._stat_field)
            now_ts = now.timestamp()
            age_seconds = now_ts - float(mtime_ts)
            return int(age_seconds // self.unit_seconds)

        self._extractor = extractor
        super().__init__(
            extractor,
            op,
            self._parse_value(value) if value is not None else None,
            requires_stat=True,
        )

    @staticmethod
    def _parse_value(value: int) -> int:
        if type(value) is not int:
            raise TypeError(
                "Age filter threshold must be an integer (fractional thresholds are not allowed)"
            )
        return value

    def __le__(self, other: int):
        return self.__class__(op=operator.le, value=self._parse_value(other))

    def __lt__(self, other: int):
        return self.__class__(op=operator.lt, value=self._parse_value(other))

    def __ge__(self, other: int):
        return self.__class__(op=operator.ge, value=self._parse_value(other))

    def __gt__(self, other: int):
        return self.__class__(op=operator.gt, value=self._parse_value(other))

    def __eq__(self, other: int):
        return self.__class__(op=operator.eq, value=self._parse_value(other))

    def __ne__(self, other: int):
        return self.__class__(op=operator.ne, value=self._parse_value(other))


class AgeMinutes(AgeBase):
    unit_seconds = 60


class AgeHours(AgeBase):
    unit_seconds = 3600


class AgeDays(AgeBase):
    unit_seconds = 86400


class AgeYears(AgeBase):
    unit_seconds = (
        86400 * 365.25
    )  # Use 365.25 days per year for compatibility with boundary tests


class AgeSeconds(AgeBase):
    unit_seconds = 1

    @staticmethod
    def _parse_value(value: int) -> int:
        if type(value) is not int:
            raise TypeError(
                "Age filter threshold must be an integer (fractional thresholds are not allowed)"
            )
        return value
