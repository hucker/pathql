"""
Base filter classes for PathQL.

Defines the abstract Filter class and logical combinators (AndFilter, OrFilter,
NotFilter) for building composable filesystem queries.
"""

import pathlib
from abc import ABC
from types import NotImplementedType

from .alias import DatetimeOrNone, StatProxyOrNone


class Filter(ABC):
    """
    Abstract base class for all PathQL filters.

    Supports logical composition via &, |, and ~ operators. Subclasses must
    implement the match() method.
    """

    def __and__(self, other: "Filter"):
        """Return a filter that matches if both filters match."""
        return AndFilter(self, other)

    def __or__(self, other: "Filter"):
        """Return a filter that matches if either filter matches."""
        return OrFilter(self, other)

    def __invert__(self):
        """Return a filter that matches if this filter does not match."""
        return NotFilter(self)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """
        Determine if the given path matches the filter criteria.  Some filters do not
        care about stat information and can just ignore the stat_proxy parameter. This
        makes testing and usage easier because you aren't required to pass in a stat value.

        Args:
            path: The pathlib.Path to check.
            stat_proxy: StatProxy for lazy stat access, or None. If stat is required and not provided, raise.
            now: Optional reference datetime for time-based filters.

        Returns:
            bool: True if the path matches, False otherwise.
        """
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Disable == operator for Filter objects."""
        raise TypeError("== operator is not supported for Filter objects.")

    def __ne__(self, other: object) -> bool:
        """Disable != operator for Filter objects."""
        raise TypeError("!= operator is not supported for Filter objects.")


class AndFilter(Filter):
    """
    Filter that matches if both left and right filters match.

    Note:
        Short-circuiting is used: if the left filter does not match, the right filter
        is not evaluated. This means that if filters have side effects, those side effects
        may not be executed. Filters should be pure functions without side effects.
    """

    def __init__(self, left: Filter, right: Filter):
        """Initialize with two filters to combine with logical AND."""
        self.left = left
        self.right = right

    def __and__(self, other: Filter | type[Filter]) -> "AndFilter | NotImplementedType":
        # Allow chaining: (Read & Write) & Execute and ((Read & Write) & (Execute & Write))
        if isinstance(other, type):
            return AndFilter(self, other())
        return AndFilter(self, other)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if both filters match the path."""
        return self.left.match(path, stat_proxy, now=now) and self.right.match(
            path, stat_proxy, now=now
        )


class OrFilter(Filter):
    """
    Filter that matches if either left or right filter matches.

    Note:
        Short-circuiting is used: if the left filter matches, the right filter
        is not evaluated. This means that if filters have side effects, those side effects
        may not be executed. Filters should be pure functions without side effects.
    """

    def __init__(self, left: Filter, right: Filter):
        """Initialize with two filters to combine with logical OR."""
        self.left: Filter = left
        self.right: Filter = right

    def __or__(self, other: Filter | type[Filter]) -> "OrFilter | NotImplementedType":
        # Allow chaining: (Read | Write) | Execute
        if isinstance(other, type):
            return OrFilter(self, other())
        return OrFilter(self, other)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if either filter matches the path."""
        return self.left.match(path, stat_proxy, now=now) or self.right.match(
            path, stat_proxy, now=now
        )


class NotFilter(Filter):
    """
    Filter that matches if the operand filter does not match.
    """

    # Does not require stat by default
    def __init__(self, operand: Filter):
        """Initialize with a filter to negate."""
        self.operand = operand

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the operand filter does not match the path."""
        return not self.operand.match(path, stat_proxy, now=now)




class All(Filter):
    """
    Filter that matches if all contained filters match (like Python's all()).

    Supports: All([f1, f2, f3]) or All(f1, f2, f3)
    Short-circuits on first failure.
    """

    def __init__(self, *filters: Filter):
        # Allow passing a single iterable or multiple filters
        if len(filters) == 1 and isinstance(filters[0], (list, tuple, set)):
            self.filters: list[Filter] = list(filters[0])
        else:
            self.filters: list[Filter] = list(filters)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if all filters match the path (short-circuits on first failure)."""
        for f in self.filters:
            if not f.match(path, stat_proxy, now=now):
                return False
        return True

class Any(Filter):
    """
    Filter that matches if any contained filter matches (like Python's any()).

    Supports: Any([f1, f2, f3]) or Any(f1, f2, f3)
    Short-circuits on first match.
    """

    def __init__(self, *filters: Filter):
        # Allow passing a single iterable or multiple filters
        if len(filters) == 1 and isinstance(filters[0], (list, tuple, set)):
            self.filters: list[Filter] = list(filters[0])
        else:
            self.filters: list[Filter] = list(filters)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if any filter matches the path (short-circuits on first match)."""
        for f in self.filters:
            if f.match(path, stat_proxy, now=now):
                return True
        return False

class AllowAll(Filter):
    """
    Lets all files pass through.  Good for testing

    Supports: AllowAll([f1, f2, f3]) or AllowAll(f1, f2, f3)

    """

    def __init__(self, *filters: Filter):
        # Just ignore filters, we aren't going to use them.  Don't depend on side effects.
        pass

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """All files pass through"""
        return True
