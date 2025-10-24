"""Filters to match values between two bounds (lower inclusive, upper exclusive)."""

import datetime as dt
import pathlib

from .alias import DatetimeOrNone
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
        filter_instance: Filter,  # Not all Filters support comparisons
        lower: int | float | dt.datetime,
        upper: int | float | dt.datetime,
    ) -> None:
        # Compose the filter using the instance, not the class
        self.filter: Filter = (filter_instance >= lower) & (filter_instance < upper)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: "StatProxy",  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the underlying between filter matches."""
        return self.filter.match(path, stat_proxy=stat_proxy, now=now)
