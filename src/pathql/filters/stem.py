"""
Stem filter for matching file stems (filename without extension) using glob patterns.
Provides declarative, pathlib-like queries for filesystem filtering.
"""

import fnmatch
import pathlib

from .alias import DatetimeOrNone
from .base import Filter


class Stem(Filter):
    """
    Filter for matching the stem (filename without extension) of a file.

    This filter mimics the behavior of `pathlib.Path.stem` and allows you to match filenames
    (without extension) against one or more glob (fnmatch) patterns. Useful for declarative
    filesystem queries.

    Example usage:
        Stem("foo")              # matches files with stem 'foo'
        Stem(["foo", "bar"])    # matches files with stem 'foo' or 'bar'
        Stem("img_*")            # matches stems like 'img_123' (glob, not regex)
        Stem("foo", ignore_case=False)  # case-sensitive match

    Args:
        patterns (str | list[str]): One or more glob patterns to match against the stem.
            Use shell-style wildcards (e.g., "foo*", "bar?").
        ignore_case (bool): If True (default), matching is case-insensitive.
    """

    def __init__(self, patterns: str | list[str], ignore_case: bool = True):
        """
        Initialize a Stem filter using fnmatch for shell-style wildcard matching.

        Args:
            patterns (str | list[str]): One or more glob patterns to match against the stem.
                If a string is provided, it is treated as a single pattern.
            ignore_case (bool, optional): If True (default), matching is case-insensitive.
                Set to False for case-sensitive matching.
        """
        if isinstance(patterns, str):
            self.patterns = [patterns]
        else:
            self.patterns = list(patterns)
        self.ignore_case = ignore_case

    def match(
        self,
        path: pathlib.Path,
        stat_proxy=None,  # Accept and ignore stat_proxy for interface consistency
        now: DatetimeOrNone = None,
    ) -> bool:
        """
        Check if the given path's stem matches any of the filter's glob patterns.
        Args:
            path (pathlib.Path): The file path to check.
            now: Ignored (for compatibility).
            stat_proxy: StatProxy (unused for stem).
        Returns:
            bool: True if the stem matches any pattern, else False.
        """
        stem = path.stem
        if self.ignore_case:
            stem = stem.lower()
            pats = [p.lower() for p in self.patterns]
        else:
            pats = self.patterns
        return any(fnmatch.fnmatchcase(stem, pat) for pat in pats)


# Alias for pathlib-like naming
Name = Stem
