"""Filters to match values between two bounds (lower inclusive, upper exclusive)."""

import datetime as dt
import pathlib

from .alias import DatetimeOrNone,StatProxyOrNone
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
        # Try the comparisons and raise clear, specific errors for common failure modes.
        # Common exceptions when calling filter_instance >= lower (or <) include:
        # - TypeError: unsupported operand types or improper implementation
        # - AttributeError: missing operator method on the object
        # - ValueError: operator raised a value error for the provided bound
        # - NotImplementedError: explicit refusal to compare
        try:
            lower_cmp = filter_instance >= lower
        except (TypeError, AttributeError, ValueError, NotImplementedError) as exc:
            raise TypeError(
                "Underlying filter of type "
                f"{type(filter_instance).__name__!r} does not support '>=' comparison "
                f"with lower bound {lower!r}."
            ) from exc

        try:
            upper_cmp = filter_instance < upper
        except (TypeError, AttributeError, ValueError, NotImplementedError) as exc:
            raise TypeError(
                "Underlying filter of type "
                f"{type(filter_instance).__name__!r} does not support '<' comparison "
                f"with upper bound {upper!r}."
            ) from exc

        # Ensure comparisons returned Filter instances
        if not isinstance(lower_cmp, Filter) or not isinstance(upper_cmp, Filter):
            raise TypeError(
                "Filter comparisons must return Filter instances. "
                f"Got {type(lower_cmp).__name__} and {type(upper_cmp).__name__} "
                f"from comparisons on {type(filter_instance).__name__!r}."
            )

        # Combine with '&' and surface combination errors clearly
        try:
            self.filter: Filter = lower_cmp & upper_cmp
        except (TypeError, AttributeError) as exc:
            raise TypeError(
                "Failed to combine comparison filters with '&' "
                f"for type {type(filter_instance).__name__!r}."
            ) from exc
        
    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the underlying between filter matches."""
        return self.filter.match(path, stat_proxy=stat_proxy, now=now)
