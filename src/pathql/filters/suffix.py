"""
Suffix filter for matching file extensions (suffixes) using glob patterns.
Supports declarative, pathlib-like queries for filesystem filtering.
Includes operator overloads and curly-brace expansion for extension sets.
"""
import pathlib
import re
import fnmatch
import logging

from .base import Filter
from .alias import DatetimeOrNone, StatResultOrNone,StrOrListOfStr

logging.basicConfig(level=logging.DEBUG)



# Metaclass for class-level operator overloads
class SuffixMeta(type):
    def __eq__(cls, other):
        """Allow Suffix == value to create a Suffix filter for that value."""
        return cls([other])
    def __ne__(cls, other):
        """Allow Suffix != value to create an empty Suffix filter (not meaningful)."""
        return cls([])  # Not meaningful, but for completeness

class Suffix(Filter, metaclass=SuffixMeta):
    """
    Filter for matching the file extension (suffix), mimics pathlib.Path.suffix (without dot).

    Accepts a string or list of extensions (e.g., Suffix("png bmp") or Suffix(["png", "bmp"]))
    and matches files with those extensions. By default, a string is split on whitespace.
    Set nosplit=True to treat the string as a single extension (for rare cases with spaces).

    Args:
        patterns (str | list[str] | None): Extensions to match (without dot).
        nosplit (bool): If True, do not split string patterns on whitespace.
    """
    def __init__(self,
                 patterns: StrOrListOfStr | None = None,
                 nosplit: bool = False,
                 ignore_case: bool = True):
        """
        Initialize a Suffix filter using fnmatch for shell-style wildcard matching.

        Args:
            patterns (str | list[str] | None): Extensions to match (without dot).
                If string and nosplit=False, splits on whitespace.
                If string contains curly braces (e.g., {img,bmp}), expands to multiple patterns.
            nosplit (bool, optional): If True, do not split string patterns on whitespace.
            ignore_case (bool, optional): If True (default), matching is case-insensitive.
        """

        self.ignore_case = ignore_case
        pats: set[str] = set()
        # Normalize patterns: strip leading dot, lowercase
        def norm(p):
            if not isinstance(p, str):
                return None
            p = p.strip().lower()
            return p if p.startswith('.') else f'.{p}'

        pats: set[str] = set()
        if isinstance(patterns, str) and not nosplit:
            brace = re.search(r"\{([^}]+)\}", patterns)
            if brace:
                base = patterns[:brace.start()]
                exts = [e.strip() for e in brace.group(1).split(",")]
                for ext in exts:
                    n = norm(base + ext)
                    if n:
                        pats.add(n)
            else:
                for e in patterns.split():
                    n = norm(e)
                    if n:
                        pats.add(n)
        elif isinstance(patterns, str):
            n = norm(patterns)
            if n:
                pats.add(n)
        elif patterns:
            for e in patterns:
                n = norm(e)
                if n:
                    pats.add(n)
        self.patterns: list[str] = [p for p in pats if p]
        self.patterns:list[str] = list(pats)
        self._fnmatch = fnmatch


    def match(self,
              path: pathlib.Path,
                now: DatetimeOrNone = None,
                stat_result: StatResultOrNone = None) -> bool:
        """
        Check if the given path's suffix matches any of the filter's extension patterns.
        Args:
            path (pathlib.Path): The file path to check.
            now: Ignored (for compatibility).
            stat_result: Optional stat result to reuse.
        Returns:
            bool: True if the suffix matches any pattern, else False.
        """
        if not self.patterns:
            raise ValueError("No file extension patterns specified.")
        fname = path.name.lower()
        for pat in self.patterns:
            if fname.endswith(pat):
                logging.debug(f"Suffix.match: {path=}, pattern={pat}, match_result=True")
                return True
        logging.debug(f"Suffix.match: {path=}, patterns={self.patterns}, match_result=False")
        return False

    def __contains__(self, item: str) -> bool:
        """Check if an extension pattern is in the filter's pattern list."""
        return item in self.patterns

    def __call__(self, *patterns: str) -> 'Suffix':
        """Allow Suffix(...) to create a new Suffix filter with given patterns."""
        # Flatten if a single list/tuple is passed
        if len(patterns) == 1 and isinstance(patterns[0], (list, tuple)):
            return Suffix(patterns[0])
        return Suffix(patterns)


    def __eq__(self, other: object) -> bool:
        """Check equality with another Suffix filter (pattern list equality)."""
        if not isinstance(other, Suffix):
            return NotImplemented
        return self.patterns == other.patterns

    def __ne__(self, other: object) -> bool:
        """Check inequality with another Suffix filter (pattern list inequality)."""
        if not isinstance(other, Suffix):
            return NotImplemented
        return self.patterns != other.patterns

    def __ror__(self, other: str | list[str]) -> 'Suffix':
        """Support set union: value | Suffix."""
        return Suffix(other)

    @classmethod
    def __class_getitem__(cls, item: str | tuple) -> 'Suffix':
        """Support Suffix[...] syntax to create a Suffix filter with given patterns."""
        if isinstance(item, tuple):
            return Suffix(item)
        return Suffix([item])


# Alias for pathlib-like naming
Ext = Suffix
Ext.__doc__ = "Alias for Suffix. See Suffix for usage.\n\n" + (Suffix.__doc__ or "")
