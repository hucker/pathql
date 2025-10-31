"""
Stem filter for PathQL.

This module provides the Stem class, which enables filtering files by their stem
(filename without extension), with support for wildcards and case-insensitive matching.

You can construct filters using:
    Stem("foo")
    Stem(["foo*", "bar*"])
    Stem() == "foo"
    Stem() == ["foo*", "bar*"]

The Stem filter is composable with other filters and supports instance-level equality
and inequality operators for expressive query building.
"""

import pathlib
import re
from typing import List, Union

from .base import Filter
from .alias import StatProxyOrNone, DatetimeOrNone

class Stem(Filter):
    """
    Filter for matching the file stem (filename without extension), supports wildcards.
    Accepts a string or list of patterns and matches files with those stems.

    Usage:
        Stem("foo")                # Old style
        Stem(["foo*", "bar*"])     # Old style, multiple patterns
        Stem() == "foo"            # New style
        Stem() == ["foo*", "bar*"] # New style, multiple patterns
        Stem() != "foo"            # Negation
    """

    def __init__(
        self,
        patterns: Union[str, List[str], None] = None,
        ignore_case: bool = True,
    ):
        """
        Args:
            patterns: Stem pattern(s) to match (e.g., "foo*", ["foo*", "bar*"]).
            ignore_case: If True, match stems case-insensitively.
        """
        self.ignore_case = ignore_case
        self.patterns = self._normalize_patterns(patterns)
        self._negate = False  # For != operator

    def _normalize_patterns(self, patterns: Union[str, List[str], None]) -> List[str]:
        """
        Normalize input patterns to a list of strings, lowercased if ignore_case is True.
        """
        if patterns is None:
            return []
        if isinstance(patterns, str):
            # Split on commas or whitespace, or treat as single pattern
            patterns = re.split(r"[,\s]+", patterns.strip())
        elif isinstance(patterns, tuple):
            patterns = list(patterns)
        elif not isinstance(patterns, list):
            patterns = [str(patterns)]
        patterns = [p for p in patterns if p]
        if self.ignore_case:
            patterns = [p.lower() for p in patterns]
        return patterns

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """
        Return True if the file's stem matches any of the patterns (supports wildcards).
        Raises ValueError if no patterns are set.
        """
        if not self.patterns:
            raise ValueError("Stem filter requires at least one pattern.")
        stem = path.stem.lower() if self.ignore_case else path.stem
        for pattern in self.patterns:
            if re.fullmatch(pattern.replace("*", ".*"), stem):
                return not self._negate
        return self._negate

    def __eq__(self, other: object):
        """
        Instance-level equality and factory behavior.
        - If `other` is a str/list/tuple, return a Stem filter from those pattern(s).
        - If `other` is a Stem, return boolean equality of normalized patterns.
        - Otherwise return NotImplemented.

        Usage:
            Stem() == "foo"
            Stem() == ["foo*", "bar*"]
        """
        if isinstance(other, str):
            obj = Stem(other, ignore_case=self.ignore_case)
            obj._negate = False
            return obj
        if isinstance(other, list):
            obj = Stem(other, ignore_case=self.ignore_case)
            obj._negate = False
            return obj
        if isinstance(other, tuple):
            obj = Stem(list(other), ignore_case=self.ignore_case)
            obj._negate = False
            return obj
        if isinstance(other, Stem):
            return self.patterns == other.patterns and self._negate == other._negate
        return NotImplemented

    def __ne__(self, other: object):
        """
        Instance-level inequality and factory behavior.
        - If `other` is a str/list/tuple, return a negated Stem filter.
        - If `other` is a Stem, return boolean inequality of patterns.
        - Otherwise return NotImplemented.

        Usage:
            Stem() != "foo"
            Stem() != ["foo*", "bar*"]
        """
        if isinstance(other, str):
            obj = Stem(other, ignore_case=self.ignore_case)
            obj._negate = True
            return obj
        if isinstance(other, list):
            obj = Stem(other, ignore_case=self.ignore_case)
            obj._negate = True
            return obj
        if isinstance(other, tuple):
            obj = Stem(list(other), ignore_case=self.ignore_case)
            obj._negate = True
            return obj
        if isinstance(other, Stem):
            return self.patterns != other.patterns or self._negate != other._negate
        return NotImplemented

    def __lt__(self, other):
        raise NotImplementedError("Stem does not support '<' operator")

    def __le__(self, other):
        raise NotImplementedError("Stem does not support '<=' operator")

    def __gt__(self, other):
        raise NotImplementedError("Stem does not support '>' operator")

    def __ge__(self, other):
        raise NotImplementedError("Stem does not support '>=' operator")

    def __xor__(self, other):
        raise NotImplementedError("Stem does not support '^' operator")

    def __mod__(self, other):
        raise NotImplementedError("Stem does not support '%' operator")

    def __floordiv__(self, other):
        raise NotImplementedError("Stem does not support '//' operator")

    def __add__(self, other):
        raise NotImplementedError("Stem does not support '+' operator")

    def __sub__(self, other):
        raise NotImplementedError("Stem does not support '-' operator")

    def __mul__(self, other):
        raise NotImplementedError("Stem does not support '*' operator")

    def __truediv__(self, other):
        raise NotImplementedError("Stem does not support '/' operator")


