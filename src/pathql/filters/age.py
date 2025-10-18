"""
age.py

Provides filter classes for querying files based on their age (time since last modification)
in minutes, hours, days, or years. These filters support declarative operator overloads,
allowing expressive queries such as `AgeDays < 10` or `AgeYears >= 1`.

Classes:
    AgeMinutes  -- Filter for file age in minutes.
    AgeHours    -- Filter for file age in hours.
    AgeDays     -- Filter for file age in days.
    AgeYears    -- Filter for file age in years.

Each filter uses a comparison operator and a threshold value, and can be used to match
files whose modification time meets the specified age criteria.

NOTE: We specificaly use modification time (mtime) for age calculations, as it is widely supported
across different operating systems and file systems. Creation time (ctime) is not consistently available
or consistant across platforms (surprisingly), so we avoid using it for age-based filters. If you must
have creation time based filtering you can build one using something like

Created < some_datetime

This will use the created time stamp and will often be correct, surprisingly working better on
Windows than on Unix-like systems.
"""

import datetime as dt
import pathlib
from typing import Callable
import operator

from .base import Filter
from .alias import DatetimeOrNone, StatResultOrNone,IntOrFloat,IntOrFloatOrNone


# Metaclass for class-level operator overloading


class AgeDays(Filter):
    """
    Filter for file age in days (since last modification).

    Allows declarative queries on file age using operator overloads:
        AgeDays < 10
        AgeDays >= 365

    Args:
        op (callable, optional): Operator function (e.g., operator.lt, operator.ge).
        value (float, optional): Value to compare file age (in days) against.
    """

    def __init__(self, op: Callable[[float, float], bool] = None, value: IntOrFloatOrNone = None) -> None:
        """
        Initialize an AgeDays filter.

        Args:
            op (Callable[[float, float], bool], optional): Operator function (e.g., operator.lt, operator.ge).
            value (float, optional): Value to compare file age (in days) against.

        Note: Only < and > operators are supported, and both are treated as inclusive (<= and >=).
        == and != are not supported and will raise TypeError.
        This should be documented in the README.
        """
        if op in (operator.eq, operator.ne):
            raise TypeError("== and != not supported for AgeDays filter. Use < or > (inclusive) only.")
        self.op = op
        self.value: float | None = float(value) if value is not None else None
    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        if self.op is None or self.value is None:
            raise TypeError("AgeDays filter not fully specified.")
        if self.op in (operator.eq, operator.ne):
            raise TypeError("== and != not supported for AgeDays filter. Use < or > (inclusive) only.")
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_result if stat_result is not None else path.stat()
            mtime_dt = dt.datetime.fromtimestamp(st.st_mtime)
            age_d = (now - mtime_dt).total_seconds() / (60 * 60 * 24)
            return self.op(age_d, self.value)
        except Exception:
            return False
    def __le__(self, other:IntOrFloat):
        return AgeDays(operator.le, other)

    def __lt__(self, other:IntOrFloat):
        return AgeDays(operator.lt, other)

    def __ge__(self, other:IntOrFloat):
        return AgeDays(operator.ge, other)

    def __gt__(self, other:IntOrFloat):
        return AgeDays(operator.gt, other)

    def __eq__(self, other:IntOrFloat):
        raise TypeError("== not supported for AgeDays filter. Use < or > (inclusive) only.")

    def __ne__(self, other:IntOrFloat):
        raise TypeError("!= not supported for AgeDays filter. Use < or > (inclusive) only.")

    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        """
        Determine if the file's age in days matches the filter criteria.

        Args:
            path: The pathlib.Path to check.
            now: Reference datetime for age calculation.
            stat_result: Optional os.stat_result for file metadata.

        Returns:
            bool: True if the file matches the age filter, False otherwise.
        """

        if self.op is None or self.value is None:
            raise TypeError("AgeDays filter not fully specified.")
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_result if stat_result is not None else path.stat()
            mtime_dt = dt.datetime.fromtimestamp(st.st_mtime)
            age_d = (now - mtime_dt).total_seconds() / (60 * 60 * 24)
            return self.op(age_d, self.value)
        except Exception:
            return False


class AgeYears(Filter):
    """
    Filter for file age in years (since last modification).

    Allows declarative queries on file age using operator overloads:
        AgeYears < 1
        AgeYears >= 5

    Args:
        op (callable, optional): Operator function (e.g., operator.lt, operator.ge).
        value (float, optional): Value to compare file age (in years) against.
    """
    def __init__(self, op: Callable[[float, float], bool] = None, value: IntOrFloatOrNone = None) -> None:
        """
        Initialize an AgeYears filter.

        Args:
            op (Callable[[float, float], bool], optional): Operator function (e.g., operator.lt, operator.ge).
            value (float, optional): Value to compare file age (in years) against.

        Note: Only < and > operators are supported, and both are treated as inclusive (<= and >=).
        == and != are not supported and will raise TypeError.
        This should be documented in the README.
        """
        if op in (operator.eq, operator.ne):
            raise TypeError("== and != not supported for AgeYears filter. Use < or > (inclusive) only.")
        self.op = op
        self.value: float | None = float(value) if value is not None else None
    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        if self.op is None or self.value is None:
            raise TypeError("AgeYears filter not fully specified.")
        if self.op in (operator.eq, operator.ne):
            raise TypeError("== and != not supported for AgeYears filter. Use < or > (inclusive) only.")
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_result if stat_result is not None else path.stat()
            mtime_dt = dt.datetime.fromtimestamp(st.st_mtime)
            age_y = (now - mtime_dt).total_seconds() / (60 * 60 * 24 * 365.25)
            return self.op(age_y, self.value)
        except Exception:
            return False
    def __le__(self, other):
        return AgeYears(operator.le, other)

    def __lt__(self, other):
        return AgeYears(operator.lt, other)

    def __ge__(self, other):
        return AgeYears(operator.ge, other)

    def __gt__(self, other):
        return AgeYears(operator.gt, other)

    def __eq__(self, other):
        raise TypeError("== not supported for AgeYears filter. Use < or > (inclusive) only.")

    def __ne__(self, other):
        raise TypeError("!= not supported for AgeYears filter. Use < or > (inclusive) only.")

    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        """
        Determine if the file's age in years matches the filter criteria.

        Args:
            path: The pathlib.Path to check.
            now: Reference datetime for age calculation.
            stat_result: Optional os.stat_result for file metadata.

        Returns:
            bool: True if the file matches the age filter, False otherwise.
        """
        if self.op is None or self.value is None:
            raise TypeError("AgeYears filter not fully specified.")
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_result if stat_result is not None else path.stat()
            mtime_dt = dt.datetime.fromtimestamp(st.st_mtime)
            age_y = (now - mtime_dt).total_seconds() / (60 * 60 * 24 * 365.25)
            return self.op(age_y, self.value)
        except Exception:
            return False



class AgeMinutes(Filter):
    """
    Filter for file age in minutes (since last modification).

    Allows declarative queries on file age using operator overloads:
        AgeMinutes < 60
        AgeMinutes >= 120

    Args:
        op (callable, optional): Operator function (e.g., operator.lt, operator.ge).
        value (float, optional): Value to compare file age (in minutes) against.
    """
    def __init__(self, op: Callable[[float, float], bool] = None, value: IntOrFloatOrNone = None) -> None:
        """
        Initialize an AgeMinutes filter.

        Args:
            op (Callable[[float, float], bool], optional): Operator function (e.g., operator.lt, operator.ge).
            value (float, optional): Value to compare file age (in minutes) against.

        Note: Only < and > operators are supported, and both are treated as inclusive (<= and >=).
        == and != are not supported and will raise TypeError.
        This should be documented in the README.
        """
        if op in (operator.eq, operator.ne):
            raise TypeError("== and != not supported for AgeMinutes filter. Use < or > (inclusive) only.")
        self.op = op
        self.value: float | None = float(value) if value is not None else None

    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        if self.op is None or self.value is None:
            raise TypeError("AgeMinutes filter not fully specified.")
        if self.op in (operator.eq, operator.ne):
            raise TypeError("== and != not supported for AgeMinutes filter. Use < or > (inclusive) only.")
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_result if stat_result is not None else path.stat()
            mtime_dt = dt.datetime.fromtimestamp(st.st_mtime)
            age_m = (now - mtime_dt).total_seconds() / 60
            return self.op(age_m, self.value)
        except Exception:
            return False

    def __le__(self, other):
        return AgeMinutes(operator.le, other)

    def __lt__(self, other):
        return AgeMinutes(operator.lt, other)

    def __ge__(self, other):
        return AgeMinutes(operator.ge, other)

    def __gt__(self, other):
        return AgeMinutes(operator.gt, other)

    def __eq__(self, other):
        raise TypeError("== not supported for AgeMinutes filter. Use < or > (inclusive) only.")

    def __ne__(self, other):
        raise TypeError("!= not supported for AgeMinutes filter. Use < or > (inclusive) only.")

    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        """
        Determine if the file's age in minutes matches the filter criteria.

        Args:
            path: The pathlib.Path to check.
            now: Reference datetime for age calculation.
            stat_result: Optional os.stat_result for file metadata.

        Returns:
            bool: True if the file matches the age filter, False otherwise.
        """
        if self.op is None or self.value is None:
            raise TypeError("AgeMinutes filter not fully specified.")
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_result if stat_result is not None else path.stat()
            mtime_dt = dt.datetime.fromtimestamp(st.st_mtime)
            age_m = (now - mtime_dt).total_seconds() / 60
            return self.op(age_m, self.value)
        except Exception:
            return False


class AgeHours(Filter):
    """
    Filter for file age in hours (since last modification).

    Allows declarative queries on file age using operator overloads:
        AgeHours < 24
        AgeHours >= 48

    Args:
        op (callable, optional): Operator function (e.g., operator.lt, operator.ge).
        value (float, optional): Value to compare file age (in hours) against.
    """
    def __init__(self, op: Callable[[float, float], bool] = None, value: IntOrFloatOrNone = None) -> None:
        """
        Initialize an AgeHours filter.

        Args:
            op (Callable[[float, float], bool], optional): Operator function (e.g., operator.lt, operator.ge).
            value (float, optional): Value to compare file age (in hours) against.

        Note: Only < and > operators are supported, and both are treated as inclusive (<= and >=).
        == and != are not supported and will raise TypeError.
        This should be documented in the README.
        """
        if op in (operator.eq, operator.ne):
            raise TypeError("== and != not supported for AgeHours filter. Use < or > (inclusive) only.")
        self.op = op
        self.value: float | None = float(value) if value is not None else None
    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        if self.op is None or self.value is None:
            raise TypeError("AgeHours filter not fully specified.")
        if self.op in (operator.eq, operator.ne):
            raise TypeError("== and != not supported for AgeHours filter. Use < or > (inclusive) only.")
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_result if stat_result is not None else path.stat()
            mtime_dt = dt.datetime.fromtimestamp(st.st_mtime)
            age_h = (now - mtime_dt).total_seconds() / 3600
            return self.op(age_h, self.value)
        except Exception:
            return False
    def __le__(self, other):
        return AgeHours(operator.le, other)

    def __lt__(self, other):
        return AgeHours(operator.lt, other)

    def __ge__(self, other):
        return AgeHours(operator.ge, other)

    def __gt__(self, other):
        return AgeHours(operator.gt, other)

    def __eq__(self, other):
        raise TypeError("== not supported for AgeHours filter. Use < or > (inclusive) only.")

    def __ne__(self, other):
        raise TypeError("!= not supported for AgeHours filter. Use < or > (inclusive) only.")

    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        """
        Determine if the file's age in hours matches the filter criteria.

        Args:
            path: The pathlib.Path to check.
            now: Reference datetime for age calculation.
            stat_result: Optional os.stat_result for file metadata.

        Returns:
            bool: True if the file matches the age filter, False otherwise.
        """
        if self.op is None or self.value is None:
            raise TypeError("AgeHours filter not fully specified.")
        try:
            if now is None:
                now = dt.datetime.now()
            st = stat_result if stat_result is not None else path.stat()
            mtime_dt = dt.datetime.fromtimestamp(st.st_mtime)
            age_h = (now - mtime_dt).total_seconds() / 3600
            return self.op(age_h, self.value)
        except Exception:
            return False