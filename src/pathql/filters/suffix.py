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
    """Filter for matching the file extension (suffix), mimics pathlib.Path.suffix (without dot).
    If given a string, splits on whitespace to allow Suffix("png bmp").
    Set nosplit=True to treat the string as a single extension (for rare cases with spaces).
    """
    def __init__(self, patterns=None, nosplit=False):
        if isinstance(patterns, str) and not nosplit:
            self.patterns = set(patterns.split())
        elif isinstance(patterns, str):
            self.patterns = {patterns}
        elif patterns:
            self.patterns = set(patterns)
        else:
            self.patterns = set()

    def match(self, path: 'pathlib.Path', now=None, stat_result=None) -> bool:
        if not self.patterns:
            raise ValueError("No file extension patterns specified.")
        # path.suffix includes the dot, so strip it
        ext = path.suffix[1:].lower() if path.suffix.startswith('.') else path.suffix.lower()
        return any(ext == pat.lower() for pat in self.patterns)

    def __contains__(self, item):
        return item in self.patterns

    def __call__(self, *patterns):
        return Suffix(patterns)

    def __eq__(self, other):
        return Suffix([other])

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

# Alias for compatibility: Ext = Suffix
Ext = Suffix
