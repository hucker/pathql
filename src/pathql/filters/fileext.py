
import pathlib
from .base import Filter
import fnmatch

class FileExt(Filter):
    def __init__(self, patterns=None):
        self.patterns = set(patterns) if patterns else set()

    def match(self, path: 'pathlib.Path') -> bool:
        if not self.patterns:
            raise ValueError("No file extension patterns specified.")
        return any(
            fnmatch.fnmatch(str(path.name).lower(), f"*.{pat.lower()}") for pat in self.patterns
        )

    def __contains__(self, item):
        return item in self.patterns

    def __call__(self, *patterns):
        return FileExt(patterns)

    def __eq__(self, other):
        return FileExt([other])

    def __ror__(self, other):
        return FileExt(other)

    def __rmul__(self, other):
        return FileExt(other)

    @classmethod
    def __class_getitem__(cls, item):
        if isinstance(item, tuple):
            return FileExt(item)
        return FileExt([item])

    def __matmul__(self, other):
        return FileExt(other)

    def __gt__(self, other):
        return FileExt(other)

    def __lt__(self, other):
        return FileExt(other)

    def __rshift__(self, other):
        return FileExt(other)

    def __rrshift__(self, other):
        return FileExt(other)

    def __rmod__(self, other):
        return FileExt(other)

    def __mod__(self, other):
        return FileExt(other)

    def __rtruediv__(self, other):
        return FileExt(other)

    def __truediv__(self, other):
        return FileExt(other)

    def __rpow__(self, other):
        return FileExt(other)

    def __pow__(self, other):
        return FileExt(other)

    def __rsub__(self, other):
        return FileExt(other)

    def __sub__(self, other):
        return FileExt(other)

    def __radd__(self, other):
        return FileExt(other)

    def __add__(self, other):
        return FileExt(other)

    def __rand__(self, other):
        return FileExt(other)

    def __and__(self, other):
        return FileExt(other)

    def __or__(self, other):
        return FileExt(other)

    def __rmatmul__(self, other):
        return FileExt(other)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return FileExt(item)
        return FileExt([item])

    def __ne__(self, other):
        return not self == other

    def __in__(self, patterns):
        return FileExt(patterns)

    def __init__(self, patterns=None):
        self.patterns = set(patterns) if patterns else set()

    def match(self, path: 'pathlib.Path') -> bool:
        if not self.patterns:
            raise ValueError("No file extension patterns specified.")
        return any(
            any(fnmatch.fnmatch(str(path.name).lower(), f"*.{pat.lower()}") for pat in self.patterns)
        )

    def __contains__(self, item):
        # Not used for our DSL
        return item in self.patterns

    def __call__(self, *patterns):
        return FileExt(patterns)

    def __eq__(self, other):
        # For syntax: FileExt == "png"
        return FileExt([other])

    def __ror__(self, other):
        # For syntax: ("png", "bmp") | FileExt
        return FileExt(other)

    def __rmul__(self, other):
        # For syntax: ["png", "bmp"] * FileExt
        return FileExt(other)

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        return obj

    def __class_getitem__(cls, item):
        # For FileExt["png", "bmp"]
        if isinstance(item, tuple):
            return FileExt(item)
        return FileExt([item])

    def __contains__(self, item):
        return item in self.patterns

    def __matmul__(self, other):
        # For FileExt @ ("png", "bmp")
        return FileExt(other)

    def __gt__(self, other):
        # For FileExt > ("png", "bmp")
        return FileExt(other)

    def __lt__(self, other):
        # For FileExt < ("png", "bmp")
        return FileExt(other)

    def __rshift__(self, other):
        # For FileExt >> ("png", "bmp")
        return FileExt(other)

    def __rrshift__(self, other):
        # For ("png", "bmp") >> FileExt
        return FileExt(other)

    def __rmod__(self, other):
        # For ("png", "bmp") % FileExt
        return FileExt(other)

    def __mod__(self, other):
        # For FileExt % ("png", "bmp")
        return FileExt(other)

    def __rtruediv__(self, other):
        # For ("png", "bmp") / FileExt
        return FileExt(other)

    def __truediv__(self, other):
        # For FileExt / ("png", "bmp")
        return FileExt(other)

    def __rpow__(self, other):
        # For ("png", "bmp") ** FileExt
        return FileExt(other)

    def __pow__(self, other):
        # For FileExt ** ("png", "bmp")
        return FileExt(other)

    def __rsub__(self, other):
        # For ("png", "bmp") - FileExt
        return FileExt(other)

    def __sub__(self, other):
        # For FileExt - ("png", "bmp")
        return FileExt(other)

    def __radd__(self, other):
        # For ("png", "bmp") + FileExt
        return FileExt(other)

    def __add__(self, other):
        # For FileExt + ("png", "bmp")
        return FileExt(other)

    def __rand__(self, other):
        # For ("png", "bmp") & FileExt
        return FileExt(other)

    def __and__(self, other):
        # For FileExt & ("png", "bmp")
        return FileExt(other)

    def __ror__(self, other):
        # For ("png", "bmp") | FileExt
        return FileExt(other)

    def __or__(self, other):
        # For FileExt | ("png", "bmp")
        return FileExt(other)

    def __rmatmul__(self, other):
        # For ("png", "bmp") @ FileExt
        return FileExt(other)

    def __getitem__(self, item):
        # For FileExt["png", "bmp"]
        if isinstance(item, tuple):
            return FileExt(item)
        return FileExt([item])

    def __call__(self, *patterns):
        return FileExt(patterns)

    def __contains__(self, item):
        return item in self.patterns

    def __eq__(self, other):
        # For FileExt == "png"
        return FileExt([other])

    def __ne__(self, other):
        return not self == other

    def __in__(self, patterns):
        # For FileExt in ("png", "bmp")
        return FileExt(patterns)
