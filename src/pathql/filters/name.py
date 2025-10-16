import pathlib
import re
from .base import Filter

class Stem(Filter):
    """Filter for matching the stem (filename without extension), mimics pathlib.Path.stem."""
    def __init__(self, pattern: str):
        self.pattern = pattern
        self._regex = re.compile(pattern, re.IGNORECASE)

    def match(self, path: 'pathlib.Path') -> bool:
        return bool(self._regex.match(path.stem))


