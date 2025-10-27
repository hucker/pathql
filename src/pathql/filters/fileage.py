"""
Filename-based age filters for PathQL.

This module provides filter classes for querying files based on the age encoded in their filenames,
rather than filesystem timestamps. Supported formats include YYYY, YYYY-MM, YYYY-MM-DD, and YYYY-MM-DD_HH,
allowing age comparisons in minutes, hours, days, or years.

These filters use floor division semantics for age calculation, matching the conventions in stat-based age filters.
They support operator overloads for expressive queries, e.g. `FilenameAgeDays < 10`.

Note: Missing date components in filenames are filled with defaults (month/day=1, hour=0) for age calculation.
"""

import datetime as dt
import math
import numbers
import operator
import pathlib
from typing import Callable

from .alias import IntOrNone, StatProxyOrNone
from .attribute_filter import AttributeFilter
from .date_filename import filename_to_datetime_parts


class FilenameAgeBase(AttributeFilter):
    unit_seconds: float = 1.0

    def __init__(
        self, op: Callable[[int, int], bool] = operator.lt, value: IntOrNone = None
    ):
        if value is not None and not isinstance(value, numbers.Integral):
            raise TypeError(
                "Fractional age thresholds are not allowed; use an integer threshold or express the value in a smaller unit."
            )

        def extractor(
            path: pathlib.Path,
            stat_proxy: StatProxyOrNone,
            now: dt.datetime | None = None,
        ) -> int:
            now = now or dt.datetime.now()
            parts = filename_to_datetime_parts(path)
            if parts is None or parts.year is None:
                return None
            file_date = dt.datetime(
                parts.year,
                parts.month if parts.month is not None else 1,
                parts.day if parts.day is not None else 1,
                parts.hour if parts.hour is not None else 0,
            )
            age_seconds = (now - file_date).total_seconds()
            return int(math.floor(age_seconds / self.unit_seconds))

        super().__init__(
            extractor,
            op,
            int(value) if value is not None else None,
            requires_stat=False,
        )

    def __le__(self, other: int):
        return self.__class__(op=operator.le, value=other)

    def __lt__(self, other: int):
        return self.__class__(op=operator.lt, value=other)

    def __ge__(self, other: int):
        return self.__class__(op=operator.ge, value=other)

    def __gt__(self, other: int):
        return self.__class__(op=operator.gt, value=other)

    def __eq__(self, other: int):
        return self.__class__(op=operator.eq, value=other)

    def __ne__(self, other: int):
        return self.__class__(op=operator.ne, value=other)


class FilenameAgeMinutes(FilenameAgeBase):
    unit_seconds = 60.0


class FilenameAgeHours(FilenameAgeBase):
    unit_seconds = 3600.0


class FilenameAgeDays(FilenameAgeBase):
    unit_seconds = 86400.0


class FilenameAgeYears(FilenameAgeBase):
    unit_seconds = 86400.0 * 365.25
    unit_seconds = 86400.0 * 365.25
