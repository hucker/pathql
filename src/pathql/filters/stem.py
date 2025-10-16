import pathlib
import re
from .base import Filter



class Stem(Filter):
    """
    Filter for matching the stem (filename without extension) of a file.

    This filter mimics the behavior of `pathlib.Path.stem` and allows you to match filenames (without extension)
    against one or more string or regex patterns. Useful for declarative filesystem queries.

    Example usage:
        Stem("foo")              # matches files with stem 'foo'
        Stem(["foo", "bar"])    # matches files with stem 'foo' or 'bar'
        Stem(r"^img_\\d+$")      # matches stems like 'img_123'
        Stem("foo", ignore_case=False)  # case-sensitive match

    Args:
        patterns (str | list[str]): One or more string or regex patterns to match against the stem.
        ignore_case (bool): If True (default), matching is case-insensitive.
    """
    def __init__(self, patterns, ignore_case=True):
        """
        Initialize a Stem filter.

        Args:
            patterns (str | list[str]): One or more string or regex patterns to match against the stem.
                If a string is provided, it is treated as a single pattern.
            ignore_case (bool, optional): If True (default), matching is case-insensitive.
                Set to False for case-sensitive matching.
        """
        if isinstance(patterns, str):
            self.patterns = [patterns]
        else:
            self.patterns = list(patterns)
        flags = re.IGNORECASE if ignore_case else 0
        self._regexes = [re.compile(p, flags) for p in self.patterns]

    def match(self, path: 'pathlib.Path', now=None, stat_result=None) -> bool:
        return any(regex.match(path.stem) for regex in self._regexes)

# Alias for pathlib-like naming
Name = Stem
