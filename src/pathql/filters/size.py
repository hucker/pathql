
import pathlib
from .base import Filter

class FilterMeta(type):
    def __le__(cls, other):
        return cls(lambda x, y: x <= y, other)
    def __lt__(cls, other):
        return cls(lambda x, y: x < y, other)
    def __ge__(cls, other):
        return cls(lambda x, y: x >= y, other)
    def __gt__(cls, other):
        return cls(lambda x, y: x > y, other)
    def __eq__(cls, other):
        return cls(lambda x, y: x == y, other)
    def __ne__(cls, other):
        return cls(lambda x, y: x != y, other)

class Size(Filter, metaclass=FilterMeta):
    def __init__(self, op=None, value=None):
        self.op = op
        self.value = value

    # Class-level operator overloads for declarative syntax
    def __class_getitem__(cls, item):
        return cls(lambda x, y: x == y, item)

    @classmethod
    def __le__(cls, other):
        return cls(lambda x, y: x <= y, other)

    @classmethod
    def __lt__(cls, other):
        return cls(lambda x, y: x < y, other)

    @classmethod
    def __ge__(cls, other):
        return cls(lambda x, y: x >= y, other)

    @classmethod
    def __gt__(cls, other):
        return cls(lambda x, y: x > y, other)

    @classmethod
    def __eq__(cls, other):
        return cls(lambda x, y: x == y, other)

    @classmethod
    def __ne__(cls, other):
        return cls(lambda x, y: x != y, other)

    def match(self, path: 'pathlib.Path', now=None, stat_result=None) -> bool:
        if self.op is None or self.value is None:
            raise ValueError("Size filter not fully specified.")
        try:
            st = stat_result if stat_result is not None else path.stat()
            size = st.st_size
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
