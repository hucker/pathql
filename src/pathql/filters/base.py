"""
Base filter classes for PathQL.

Defines the abstract Filter class and logical combinators (AndFilter, OrFilter,
NotFilter) for building composable filesystem queries.
"""

import pathlib
from .alias import DatetimeOrNone, StatResultOrNone


class Filter:
    """
    Abstract base class for all PathQL filters.

    Supports logical composition via &, |, and ~ operators. Subclasses must
    implement the match() method.
    """
    def __and__(self, other: 'Filter'):
        """Return a filter that matches if both filters match."""
        return AndFilter(self, other)

    def __or__(self, other: 'Filter'):
        """Return a filter that matches if either filter matches."""
        return OrFilter(self, other)

    def __invert__(self):
        """Return a filter that matches if this filter does not match."""
        return NotFilter(self)

    def match(self, path: pathlib.Path, now: DatetimeOrNone = None,
              stat_result: StatResultOrNone = None) -> bool:
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
    """
    def __init__(self, left: Filter, right: Filter):
        """Initialize with two filters to combine with logical AND."""
        self.left = left
        self.right = right

    def __and__(self, other):
        # Allow chaining: (Read & Write) & Execute and ((Read & Write) & (Execute & Write))
        if isinstance(other, type) and issubclass(other, Filter):
            return AndFilter(self, other())
        if isinstance(other, Filter):
            return AndFilter(self, other)
        if isinstance(other, AndFilter):
            return AndFilter(self, other)
        return NotImplemented
    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None
    ) -> bool:
        """Return True if both filters match the path."""
        return self.left.match(path, now=now, stat_result=stat_result) and self.right.match(path, now=now, stat_result=stat_result)

class OrFilter(Filter):
    def __or__(self, other):
        # Allow chaining: (Read | Write) | Execute
        if isinstance(other, type) and issubclass(other, Filter):
            return OrFilter(self, other())
        if isinstance(other, Filter):
            return OrFilter(self, other)
        return NotImplemented
    """
    Filter that matches if either left or right filter matches.
    """
    def __init__(self, left: Filter, right: Filter):
        """Initialize with two filters to combine with logical OR."""
        self.left = left
        self.right = right
    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result:StatResultOrNone = None
    ) -> bool:
        """Return True if either filter matches the path."""
        return self.left.match(path, now=now, stat_result=stat_result) or self.right.match(path, now=now, stat_result=stat_result)

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
        stat_result: StatResultOrNone = None
    ) -> bool:
        """Return True if the operand filter does not match the path."""
        return not self.operand.match(path, now=now, stat_result=stat_result)
