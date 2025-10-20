import pathlib
from typing import Callable, Any
from types import NotImplementedType
from .alias import StatResultOrNone, IntOrNone
from .base import Filter


class Size(Filter):
    """
    Filter for file size (in bytes).

    Allows declarative queries on file size using operator overloads:
        Size() <= 1024
        Size() > 1_000_000
        Size(lambda x, y: x % 2 == 0, None)  # custom logic

    Args:
        op (callable, optional): Operator function (e.g., operator.le, operator.gt).
        value (int, optional): Value to compare file size against.
    """
    def __init__(self, op: Callable[[Any, Any], bool] = None, value: IntOrNone = None) -> None:
        self.op: Callable[[Any, Any], bool] = op
        self.value: int | None = value

    def match(self, path: pathlib.Path, now=None, stat_result: StatResultOrNone = None) -> bool:
        if self.op is None or self.value is None:
            raise TypeError("Size filter not fully specified.")
        try:
            st = stat_result if stat_result is not None else path.stat()
            size: int = st.st_size
            return self.op(size, self.value)
        except Exception:
            return False

    def __le__(self, other: object) -> 'Size | NotImplementedType':
        if not isinstance(other, int):
            return NotImplemented
        if other < 0:
            raise ValueError("size must be non-negative")
        return Size(lambda x, y: x <= y, other)

    def __lt__(self, other: object) -> 'Size | NotImplementedType':
        if not isinstance(other, int):
            return NotImplemented
        if other < 0:
            raise ValueError("size must be non-negative")
        return Size(lambda x, y: x < y, other)

    def __ge__(self, other: object) -> 'Size | NotImplementedType':
        if not isinstance(other, int):
            return NotImplemented
        if other < 0:
            raise ValueError("size must be non-negative")
        return Size(lambda x, y: x >= y, other)

    def __gt__(self, other: object) -> 'Size | NotImplementedType':
        if not isinstance(other, int):
            return NotImplemented
        if other < 0:
            raise ValueError("size must be non-negative")
        return Size(lambda x, y: x > y, other)

    def __eq__(self, other: object) -> 'Size | NotImplementedType':
        if not isinstance(other, int):
            return NotImplemented
        if other < 0:
            raise ValueError("size must be non-negative")
        return Size(lambda x, y: x == y, other)

    def __ne__(self, other: object) -> 'Size | NotImplementedType':
        if not isinstance(other, int):
            return NotImplemented
        if other < 0:
            raise ValueError("size must be non-negative")
        return Size(lambda x, y: x != y, other)
