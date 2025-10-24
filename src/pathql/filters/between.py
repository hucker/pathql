"""Filters to match values between two bounds (lower inclusive, upper exclusive)."""

import pathlib
import datetime as dt

from .alias import DatetimeOrNone, NumericFilterType, StatResultOrNone
from .base import Filter


class Between(Filter):
    """
    Filter matches if value between bounds: inclusive on lower bound, exclusive on upper bound.

    Usage:
        Between(AgeHours, 2, 3)  # Equivalent to (AgeHours >= 2) & (AgeHours < 3)

    This matches values x such that lower <= x < upper.
    """

    def __init__(
        self,
        filter_instance:Filter,  # Not all Filters support comparisons
        lower: int | float| dt.datetime,
        upper: int | float| dt.datetime
    ) -> None:
          # Compose the filter using the instance, not the class
        self.filter = (filter_instance >= lower) & (filter_instance < upper)

    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """Return True if the underlying between filter matches."""
        return self.filter.match(path, now=now, stat_result=stat_result)

    def needs_stat(self) -> bool:
        """Return True if the underlying filter requires stat data."""

        # Between depends on what the underlying filter needs
        return self.filter.needs_stat()