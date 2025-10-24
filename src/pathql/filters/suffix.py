"""
Suffix filter for PathQL.

This module provides the Suffix class, which enables filtering files by their extension
(similar to pathlib.Path.suffix, but without the dot). Suffix supports matching against
single or multiple extensions, with case-insensitive comparison by default.

You can construct filters using:
    Suffix("txt")
    Suffix(["log", "txt"])
    Suffix() == "csv"
    Suffix() == ["csv", "tsv"]

The Suffix filter is composable with other filters and supports instance-level equality
and inequality operators for expressive query building.
"""

import pathlib
import re
from typing import List

from .alias import DatetimeOrNone, StrOrListOfStr
from .base import Filter
from .proxy_not_needed import ProxyNotNeededTriggersExceptionOnUsage
from .stat_proxy import StatProxy


class Suffix(Filter):
    """
    Filter for matching the file extension (suffix), mimics pathlib.Path.suffix (without dot).
    Accepts a string or list of extensions and matches files with those extensions.
    """

    def __init__(
        self,
        patterns: StrOrListOfStr | None = None,
        nosplit: bool = False,
        ignore_case: bool = True,
    ):
        """
        Args:
            patterns: Extension(s) to match (e.g., "txt", ["log", "txt"]).
            nosplit: If True, do not split on commas in patterns.
            ignore_case: If True, match extensions case-insensitively.
        """
        self.nosplit = nosplit
        self.ignore_case = ignore_case
        self.patterns = self._normalize_patterns(patterns)
        if not self.patterns:
            raise ValueError("Suffix filter requires at least one pattern.")

    def _normalize_patterns(self, patterns: StrOrListOfStr | None) -> List[str]:
        if patterns is None:
            return []
        if isinstance(patterns, str):
            # Brace expansion: "{foo,,fum}" -> ["foo", "fum"]
            brace_match = re.match(r"^\{(.+)\}$", patterns.strip())
            if brace_match:
                patterns = brace_match.group(1).split(",")
            elif not self.nosplit:
                patterns = re.split(r"[,\s]+", patterns.strip())
            else:
                patterns = [patterns]
        elif isinstance(patterns, tuple):
            patterns = list(patterns)
        elif not isinstance(patterns, list):
            patterns = [str(patterns)]
        # Remove empty strings and strip leading dots
        patterns = [p[1:] if p.startswith(".") else p for p in patterns if p]
        if self.ignore_case:
            patterns = [p.lower() for p in patterns]
        return patterns

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxy | None = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """
        Return True if the file's name ends with any of the patterns (with dot prefix).
        Supports multi-part extensions.
        """  # If stat_proxy is not provided, use a dummy proxy that raises if accessed
        if stat_proxy is None:
            stat_proxy = ProxyNotNeededTriggersExceptionOnUsage(path)

        filename = path.name.lower() if self.ignore_case else path.name
        for pattern in self.patterns:
            # Ensure pattern starts with a dot
            dot_pattern = f".{pattern}" if not pattern.startswith(".") else pattern
            if filename.endswith(dot_pattern):
                return True
        return False

    def __eq__(self, other: object):
        """
        Instance-level equality and factory behavior.
        - If `other` is a str/list/tuple, return a new Suffix filter constructed from that pattern(s).
        - If `other` is a Suffix, return boolean equality of normalized patterns.
        - Otherwise return NotImplemented.
        """
        if isinstance(other, str):
            return Suffix(other, nosplit=self.nosplit, ignore_case=self.ignore_case)
        if isinstance(other, list):
            return Suffix(other, nosplit=self.nosplit, ignore_case=self.ignore_case)
        if isinstance(other, tuple):
            return Suffix(
                list(other), nosplit=self.nosplit, ignore_case=self.ignore_case
            )
        if isinstance(other, Suffix):
            return self.patterns == other.patterns
        return NotImplemented

    def __ne__(self, other: object):
        """
        Instance-level inequality and factory behavior.
        - If `other` is a str/list/tuple, return an empty Suffix filter.
        - If `other` is a Suffix, return boolean inequality of patterns.
        - Otherwise return NotImplemented.
        """
        if isinstance(other, (str, list, tuple)):
            return Suffix([], nosplit=self.nosplit, ignore_case=self.ignore_case)
        if isinstance(other, Suffix):
            return self.patterns != other.patterns
        return NotImplemented


# Alias for pathlib-like naming
Ext = Suffix
Ext.__doc__ = "Alias for Suffix. See Suffix for usage.\n\n" + (Suffix.__doc__ or "")
Ext.__doc__ = "Alias for Suffix. See Suffix for usage.\n\n" + (Suffix.__doc__ or "")
