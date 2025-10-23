"""
Base filter classes for PathQL.

Defines the abstract Filter class and logical combinators (AndFilter, OrFilter,
NotFilter) for building composable filesystem queries.
"""

import pathlib
from types import NotImplementedType

from .alias import DatetimeOrNone, StatResultOrNone


class Filter:
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
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """
        Determine if the given path matches the filter criteria.

        Args:
            path: The pathlib.Path to check.
            now: Optional reference datetime for time-based filters.
            stat_result: Optional os.stat_result for file metadata.

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
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """Return True if both filters match the path."""
        return self.left.match(
            path, now=now, stat_result=stat_result
        ) and self.right.match(path, now=now, stat_result=stat_result)


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
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """Return True if either filter matches the path."""
        return self.left.match(
            path, now=now, stat_result=stat_result
        ) or self.right.match(path, now=now, stat_result=stat_result)


class NotFilter(Filter):
    """
    Filter that matches if the operand filter does not match.
    """

    def __init__(self, operand: Filter):
        """Initialize with a filter to negate."""
        self.operand = operand

    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """Return True if the operand filter does not match the path."""
        return not self.operand.match(path, now=now, stat_result=stat_result)
        return not self.operand.match(path, now=now, stat_result=stat_result)
