"""Filter for matching filenames using shell-style glob patterns."""

import fnmatch
import pathlib

from .alias import DatetimeOrNone
from .base import Filter


class File(Filter):
    """Match a file's name using a shell-style glob pattern."""

    def __init__(
        self,
        pattern: str,
        ignore_case: bool = True,
    ) -> None:
        """Create a File filter.

        Pattern matching is case-insensitive by default.
        """
        self.pattern = pattern.lower() if ignore_case else pattern
        self.ignore_case = ignore_case

    def match(
        self,
        path: pathlib.Path,
        stat_proxy=None,  # Accept and ignore stat_proxy for interface consistency
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the filename matches the configured pattern."""
        fname = path.name.lower() if self.ignore_case else path.name
        return fnmatch.fnmatch(fname, self.pattern)
