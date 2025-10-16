
import pathlib
from .base import Filter

class Size(Filter):
    def __init__(self, op=None, value=None):
        self.op = op
        self.value = value

    def match(self, path: 'pathlib.Path') -> bool:
        if self.op is None or self.value is None:
            raise ValueError("Size filter not fully specified.")
        try:
            size = path.stat().st_size
            return self.op(size, self.value)
        except Exception:
            return False

    def __le__(self, other):
        return Size.__new__(Size, lambda x, y: x <= y, other)
    def __lt__(self, other):
        return Size.__new__(Size, lambda x, y: x < y, other)
    def __ge__(self, other):
        return Size.__new__(Size, lambda x, y: x >= y, other)
    def __gt__(self, other):
        return Size.__new__(Size, lambda x, y: x > y, other)
    def __eq__(self, other):
        return Size.__new__(Size, lambda x, y: x == y, other)
    def __ne__(self, other):
        return Size.__new__(Size, lambda x, y: x != y, other)
