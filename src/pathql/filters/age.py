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

import datetime as dt
import math
import numbers
import operator
import pathlib
from typing import Callable

from .alias import DatetimeOrNone, IntOrFloat, IntOrFloatOrNone, IntOrNone
from .base import Filter
from .datetime_parts import normalize_attr
from .stat_proxy import StatProxy


class AgeBase(Filter):
    """Base for unit-rounded age filters.

    Subclasses must set `unit_seconds` to the number of seconds in the unit
    (minutes=60, hours=3600, days=86400, years≈365.25*86400). The filter
    computes the file age in seconds, converts to an integer unit count by
    floor(age_seconds / unit_seconds), and applies the comparison operator
    against the integer unit age.
    """

    # All age filters require stat data to function.

    unit_seconds: float = 1.0

    def __init__(
        self,
        op: Callable[[float, float], bool] = operator.lt,
        value: IntOrFloatOrNone = None,
        *,
        attr: str = "modified",
    ) -> None:
        # comparisons operate on integer unit ages
        self.op = op
        # Disallow fractional thresholds. If callers need fractional time
        # they should express the same threshold in a smaller unit (e.g. 2.5
        # hours -> 150 minutes).
        if value is None:
            self.value: IntOrNone = None
        else:
            if not isinstance(value, numbers.Integral):
                raise TypeError(
                    "Fractional age thresholds are not allowed; "
                    "use an integer threshold or express the value in a smaller unit "
                    "(e.g. 2.5 hours -> 150 minutes)."
                )
            self.value = int(value)
        # which stat attribute to use (st_mtime/st_atime/st_ctime)
        # default is 'modified' -> st_mtime. Use the canonical normalizer from datetime_parts.
        self.attr = attr
        self._stat_field = normalize_attr(attr)

    def _unit_age(self, now: dt.datetime, mtime_ts: float) -> int:
        age_seconds = (now - dt.datetime.fromtimestamp(mtime_ts)).total_seconds()
        # floor division semantics: 0..unit_seconds-1 -> 0, unit_seconds..2*unit_seconds-1 -> 1, etc.
        return int(math.floor(age_seconds / self.unit_seconds))

    def __le__(self, other: IntOrFloat):
        # Require an instance for comparisons (disallow `AgeDays <= 5`)
        if isinstance(self, type):
            raise TypeError(
                f"{self.__name__} must be instantiated before comparison; use {self.__name__}() <= value"
            )
        cls_obj = self.__class__
        return cls_obj(
            op=operator.le, value=other, attr=getattr(self, "attr", "modified")
        )

    def __lt__(self, other: IntOrFloat):
        if isinstance(self, type):
            raise TypeError(
                f"{self.__name__} must be instantiated before comparison; use {self.__name__}() < value"
            )
        cls_obj = self.__class__
        return cls_obj(
            op=operator.lt, value=other, attr=getattr(self, "attr", "modified")
        )

    def __ge__(self, other: IntOrFloat):
        if isinstance(self, type):
            raise TypeError(
                f"{self.__name__} must be instantiated before comparison; use {self.__name__}() >= value"
            )
        cls_obj = self.__class__
        return cls_obj(
            op=operator.ge, value=other, attr=getattr(self, "attr", "modified")
        )

    def __gt__(self, other: IntOrFloat):
        if isinstance(self, type):
            raise TypeError(
                f"{self.__name__} must be instantiated before comparison; use {self.__name__}() > value"
            )
        cls_obj = self.__class__
        return cls_obj(
            op=operator.gt, value=other, attr=getattr(self, "attr", "modified")
        )

    def __eq__(self, other: IntOrFloat):  # type: ignore[override]
        if isinstance(self, type):
            raise TypeError(
                f"{self.__name__} must be instantiated before comparison; use {self.__name__}() == value"
            )
        cls_obj = self.__class__
        return cls_obj(
            op=operator.eq, value=other, attr=getattr(self, "attr", "modified")
        )

    def __ne__(self, other: IntOrFloat):  # type: ignore[override]
        if isinstance(self, type):
            raise TypeError(
                f"{self.__name__} must be instantiated before comparison; use {self.__name__}() != value"
            )
        cls_obj = self.__class__
        return cls_obj(
            op=operator.ne, value=other, attr=getattr(self, "attr", "modified")
        )

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxy | None = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """Evaluate the filter against a path.

        Semantics: compute the file age in seconds relative to `now` (defaults to
        current time), convert to the configured unit (via `unit_seconds`) and
        floor to an integer unit count. The operator is applied to the integer
        unit age and the integer form of the configured threshold. For example:

            - For `AgeDays`: unit_age == 0 means file age < 1 day.
            - `AgeDays == 0` matches files with age >= 0 and < 1 day.
            - `AgeHours <= 2` matches files with unit_age 0, 1, or 2 (i.e., < 3 hours).

        Returns True if the comparison holds, False on any stat/io error.
        """
        if self.op is None or self.value is None:
            raise TypeError(f"{self.__class__.__name__} filter not fully specified.")
        if stat_proxy is None:
            raise ValueError(
                f"{self.__class__.__name__} filter requires stat_proxy, but none was provided."
            )
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_proxy.stat()
            # resolve which stat field to use
            stat_field = getattr(self, "_stat_field", "st_mtime")
            mtime_ts = getattr(st, stat_field)
            unit_age = self._unit_age(now, mtime_ts)
            return bool(self.op(unit_age, int(self.value)))
        except (OSError, ValueError):
            return False


class AgeMinutes(AgeBase):
    """Filter matching file age in whole minutes.

    The file's age is converted to minutes and floored to an integer value.
    Comparisons operate on that integer minute count. Example usage:

        AgeMinutes == 0   # files younger than 1 minute
        AgeMinutes <= 5   # files up to 5 minutes old (0..5)
    """

    unit_seconds = 60.0


class AgeSeconds(AgeBase):
    """Filter matching file age in whole seconds.

    The file's age is converted to seconds and floored to an integer value.
    Comparisons operate on that integer second count. Example usage:

        AgeSeconds == 0   # files younger than 1 second
        AgeSeconds > 20   # files older than 20 seconds
    """

    unit_seconds = 1.0


class AgeHours(AgeBase):
    """Filter matching file age in whole hours.

    The file's age is converted to hours and floored to an integer value.
    Comparisons operate on that integer hour count. Example usage:

        AgeHours == 0   # files younger than 1 hour
        AgeHours >= 24  # files at least 24 hours old
    """

    unit_seconds = 3600.0


class AgeDays(AgeBase):
    """Filter matching file age in whole days.

    The file's age is converted to days and floored to an integer value.
    Comparisons operate on that integer day count. Example usage:

        AgeDays == 0   # files younger than 1 day
        AgeDays > 365  # files older than 365 days
    """

    unit_seconds = 60.0 * 60.0 * 24.0


class AgeYears(AgeBase):
    """Filter matching file age in whole years (approximate).

    Years are approximated using 365.25 days per year; age is floored to an
    integer year count before comparison. Use for coarse-grained year-based
    queries (not for precise calendrical arithmetic).
    """

    unit_seconds = 60.0 * 60.0 * 24.0 * 365.25
    unit_seconds = 60.0 * 60.0 * 24.0 * 365.25
