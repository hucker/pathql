import pathlib
from .base import Filter
import fnmatch



# Metaclass for class-level operator overloads
class SuffixMeta(type):
    def __eq__(cls, other):
        return cls([other])
    def __ne__(cls, other):
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
    def __init__(self, patterns=None, nosplit=False, ignore_case=True):
        """
        Initialize a Suffix filter using fnmatch for shell-style wildcard matching.

        Args:
            patterns (str | list[str] | None): Extensions to match (without dot).
                If a string and nosplit=False, splits on whitespace.
                If a string contains curly braces (e.g., {img,bmp,jpg}), expands to multiple patterns.
            nosplit (bool, optional): If True, do not split string patterns on whitespace.
            ignore_case (bool, optional): If True (default), matching is case-insensitive.
        """
        import fnmatch
        self.ignore_case = ignore_case
        pats = set()
        if isinstance(patterns, str) and not nosplit:
            # Expand curly-brace sets: foo.{img,bmp,jpg} -> foo.img, foo.bmp, foo.jpg
            import re
            brace = re.search(r"\{([^}]+)\}", patterns)
            if brace:
                base = patterns[:brace.start()]
                exts = [e.strip() for e in brace.group(1).split(",")]
                for ext in exts:
                    pats.add(base + ext)
            else:
                pats.update(patterns.split())
        elif isinstance(patterns, str):
            pats.add(patterns)
        elif patterns:
            pats.update(patterns)
        self.patterns = list(pats)
        self._fnmatch = fnmatch



    def match(self, path: 'pathlib.Path', now=None, stat_result=None) -> bool:
        if not self.patterns:
            raise ValueError("No file extension patterns specified.")
        # path.suffix includes the dot, so strip it
        ext = path.suffix[1:] if path.suffix.startswith('.') else path.suffix
        if self.ignore_case:
            ext = ext.lower()
            pats = [p.lower() for p in self.patterns]
        else:
            pats = self.patterns
        return any(self._fnmatch.fnmatchcase(ext, pat) for pat in pats)

    def __contains__(self, item):
        return item in self.patterns

    def __call__(self, *patterns):
        # Flatten if a single list/tuple is passed
        if len(patterns) == 1 and isinstance(patterns[0], (list, tuple)):
            return Suffix(patterns[0])
        return Suffix(patterns)


    def __eq__(self, other):
        if not isinstance(other, Suffix):
            return NotImplemented
        return self.patterns == other.patterns

    def __ne__(self, other):
        if not isinstance(other, Suffix):
            return NotImplemented
        return self.patterns != other.patterns

    def __ror__(self, other):
        return Suffix(other)

    def __rmul__(self, other):
        return Suffix(other)

    @classmethod
    def __class_getitem__(cls, item):
        if isinstance(item, tuple):
            return Suffix(item)
        return Suffix([item])

    def __matmul__(self, other):
        return Suffix(other)

    def __gt__(self, other):
        return Suffix(other)

    def __lt__(self, other):
        return Suffix(other)

    def __rshift__(self, other):
        return Suffix(other)

    def __rrshift__(self, other):
        return Suffix(other)

    def __rmod__(self, other):
        return Suffix(other)

    def __mod__(self, other):
        return Suffix(other)

    def __rtruediv__(self, other):
        return Suffix(other)

# Alias for pathlib-like naming
Ext = Suffix
Ext.__doc__ = "Alias for Suffix. See Suffix for usage."
Ext = Suffix
