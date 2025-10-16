import pathlib
import re
from .base import Filter



class Stem(Filter):
    """Filter for matching the stem (filename without extension), mimics pathlib.Path.stem.
    Accepts a list of patterns or a string (which is turned into a list with a single string).
    Optionally, set ignore_case=False for case-sensitive matching.
    """
    def __init__(self, patterns, ignore_case=True):
        if isinstance(patterns, str):
            self.patterns = [patterns]
        else:
            self.patterns = list(patterns)
        flags = re.IGNORECASE if ignore_case else 0
        self._regexes = [re.compile(p, flags) for p in self.patterns]

    def match(self, path: 'pathlib.Path', now=None) -> bool:
        return any(regex.match(path.stem) for regex in self._regexes)

Name = Stem
Name = Stem
