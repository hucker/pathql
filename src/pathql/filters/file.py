import pathlib
import fnmatch
from .base import Filter
from .alias import DatetimeOrNone, StatResultOrNone

class File(Filter):
    """
    Filter for matching a file's full name using shell-style globbing (fnmatch).

    This filter matches the given pattern against the entire filename using fnmatch.
    Wildcards (*, ?) are supported. Curly-brace expansion is NOT supported.
    """
    def __init__(self, pattern: str, ignore_case: bool = True):
        self.pattern = pattern.lower() if ignore_case else pattern
        self.ignore_case = ignore_case

    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None):
        fname = path.name.lower() if self.ignore_case else path.name
        return fnmatch.fnmatch(fname, self.pattern)
