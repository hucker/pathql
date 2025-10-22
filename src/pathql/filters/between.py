"""Filters to match values between two bounds (lower inclusive, upper exclusive)."""

import pathlib

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
        filter_cls: NumericFilterType,  # Not all Filters support comparisons
        lower: int | float,
        upper: int | float,
    ) -> None:
        """Create a Between filter from a Filter class and bounds."""
        self.filter: Filter = (filter_cls() >= lower) & (filter_cls() < upper)

    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """Return True if the underlying between filter matches."""
        return self.filter.match(path, now=now, stat_result=stat_result)
