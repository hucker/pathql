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

from .alias import IntOrNone
from .date_filename import filename_to_datetime_parts


class FilenameAgeBase:
    """Base for unit-rounded filename age filters."""

    # This class requires stat data to function
    requires_stat: bool = True

    unit_seconds: float = 1.0

    def __init__(
        self,
        op: Callable[[float, float], bool] = operator.lt,
        value: IntOrNone = None,
    ) -> None:
        self.op = op
        if value is None:
            self.value: IntOrNone = None
        else:
            if not isinstance(value, numbers.Integral):
                raise TypeError(
                    "Fractional age thresholds are not allowed; "
                    "use an integer threshold or express the value in a smaller unit."
                )
            self.value = int(value)

    def _unit_age(self, now: dt.datetime, file_date: dt.datetime) -> int:
        # floor division semantics: 0..unit_seconds-1 -> 0, unit_seconds..2*unit_seconds-1 -> 1, etc.
        age_seconds = (now - file_date).total_seconds()
        return int(math.floor(age_seconds / self.unit_seconds))

    def __le__(self, other: int):
        return self.__class__(op=operator.le, value=other)

    def __lt__(self, other: int):
        stat_proxy = (None,)  # Accept and ignore stat_proxy for interface consistency
        now: dt.datetime | None = (None,)

    def __ge__(self, other: int):
        return self.__class__(op=operator.ge, value=other)

    def __gt__(self, other: int):
        return self.__class__(op=operator.gt, value=other)

    def __eq__(self, other: int):  # type: ignore[override]
        return self.__class__(op=operator.eq, value=other)

    def __ne__(self, other: int):  # type: ignore[override]
        return self.__class__(op=operator.ne, value=other)

    def match(
        self,
        path: pathlib.Path,
        now: dt.datetime | None = None,
    ) -> bool:
        """Evaluate the filter against a path using filename date.

        Semantics: compute the file age in seconds relative to `now` (defaults to
        current time), convert to the configured unit (via `unit_seconds`) and
        floor to an integer unit count. The operator is applied to the integer
        unit age and the integer form of the configured threshold.

        Returns True if the comparison holds, False if no date can be extracted.
        """
        if self.op is None or self.value is None:
            raise TypeError(f"{self.__class__.__name__} filter not fully specified.")
        now = now or dt.datetime.now()
        parts = filename_to_datetime_parts(path)
        if parts is None or parts.year is None:
            return False
        # Fill missing parts with 1 for month/day, 0 for hour (matches AgeBase convention)
        file_date = dt.datetime(
            parts.year,
            parts.month if parts.month is not None else 1,
            parts.day if parts.day is not None else 1,
            parts.hour if parts.hour is not None else 0,
        )
        unit_age = self._unit_age(now, file_date)
        return bool(self.op(unit_age, int(self.value)))


class FilenameAgeMinutes(FilenameAgeBase):
    """Filter matching file age in whole minutes (from filename)."""

    unit_seconds = 60.0


class FilenameAgeHours(FilenameAgeBase):
    """Filter matching file age in whole hours (from filename)."""

    unit_seconds = 3600.0


class FilenameAgeDays(FilenameAgeBase):
    """Filter matching file age in whole days (from filename)."""

    unit_seconds = 86400.0


class FilenameAgeYears(FilenameAgeBase):
    """Filter matching file age in whole years (from filename)."""

    unit_seconds = 86400.0 * 365.25
