
import datetime as dt
import os
import pathlib
from .base import Filter
from .stem import Stem
from .suffix import Suffix

class File(Filter):
    """
    Filter for matching a file's full name by composing Stem and Suffix filters.

    This filter splits the given pattern (a filename or Path) into its stem and suffix parts,
    and matches both using the Stem and Suffix filters. All pattern logic (wildcards, regex, etc.)
    is delegated to those filters. This class is purely compositional and does not implement
    any matching logic itself.
    """
    def __init__(self, pattern:str, ignore_case:bool=True):
        """
        Initialize a File filter by splitting the pattern into stem and suffix.

        Args:
            pattern (str | Path): The file name or Path to match. Can be a string or a Path object.
            ignore_case (bool): Whether to ignore case when matching the stem. Default: True.
        """
        self.pattern = pattern
        self.ignore_case = ignore_case
        if isinstance(pattern, pathlib.Path):
            p = pattern
        else:
            p = pathlib.Path(pattern)
        stem = p.stem
        suffix = p.suffix[1:] if p.suffix.startswith('.') else p.suffix
        self.stem_filter = Stem(stem, ignore_case=ignore_case)
        self.suffix_filter = Suffix(suffix) if suffix else None

    def match(self, path: 'pathlib.Path', now:dt.datetime|None=None, stat_result:os.stat_result|None=None):
        """
        Return True if the given path matches both the stem and suffix filters.

        Args:
            path (Path): The file path to test.
            now, stat_result: Passed through to underlying filters (for compatibility).
        """
        if self.suffix_filter:
            return self.stem_filter.match(path, now=now, stat_result=stat_result) and self.suffix_filter.match(path, now=now, stat_result=stat_result)
        return self.stem_filter.match(path, now=now, stat_result=stat_result)

    def as_stem_and_suffix(self):
        """
        Return the underlying Stem and Suffix filter objects as a tuple, but only if the pattern is literal (no wildcards).

        Returns:
            tuple: (Stem, Suffix) if both are present and pattern is literal, or (Stem,) if only stem is present and literal.
            None if the pattern contains wildcards (e.g., *, ?, [, ]).

        This is useful for introspection or for composing with other filters.
        """
        # Check for wildcards in the original pattern string
        pat = str(self.pattern)
        if any(c in pat for c in '*?[]{}'):
            return None
        if self.suffix_filter:
            return (self.stem_filter, self.suffix_filter)
        return (self.stem_filter,)
