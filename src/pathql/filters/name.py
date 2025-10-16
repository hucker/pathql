import pathlib
import re
from .base import Filter

class Name(Filter):
    def __init__(self, pattern: str):
        self.pattern = pattern
        self._regex = re.compile(pattern, re.IGNORECASE)

    def match(self, path: 'pathlib.Path') -> bool:
        return bool(self._regex.match(path.name))
