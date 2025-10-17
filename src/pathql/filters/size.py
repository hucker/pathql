import pathlib
from .base import Filter
from typing import Callable, Type, Any

class FilterMeta(type):
    def __le__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x <= y, other)
    def __lt__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x < y, other)
    def __ge__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x >= y, other)
    def __gt__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x > y, other)
    def __eq__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x == y, other)
    def __ne__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x != y, other)

class Size(Filter, metaclass=FilterMeta):
    """
    Filter for file size (in bytes).

    Allows declarative queries on file size using operator overloads:
        Size <= 1024
        Size > 1_000_000
        Size(lambda x, y: x % 2 == 0, None)  # custom logic

    Args:
        op (callable, optional): Operator function (e.g., operator.le, operator.gt).
        value (int, optional): Value to compare file size against.
    """
    def __init__(self, op: Callable[[Any, Any], bool] = None, value: int | None = None) -> None:
        """
        Initialize a Size filter.

        Args:
            op (callable, optional): Operator function (e.g., operator.le, operator.gt).
            value (int, optional): Value to compare file size against.
        """
        self.op: Callable[[Any, Any], bool] | None = op
        self.value: int | None = value

    # Class-level operator overloads for declarative syntax
    def __class_getitem__(cls: Type['Size'], item: int) -> 'Size':
        return cls(lambda x, y: x == y, item)

    @classmethod
    def __le__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x <= y, other)

    @classmethod
    def __lt__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x < y, other)

    @classmethod
    def __ge__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x >= y, other)

    @classmethod
    def __gt__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x > y, other)

    @classmethod
    def __eq__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x == y, other)

    @classmethod
    def __ne__(cls: Type['Size'], other: int) -> 'Size':
        return cls(lambda x, y: x != y, other)

    def match(self, path: pathlib.Path, now: float | None = None, stat_result: object = None) -> bool:
        if self.op is None or self.value is None:
            raise ValueError("Size filter not fully specified.")
        try:
            st = stat_result if stat_result is not None else path.stat()
            size: int = st.st_size
            return self.op(size, self.value)
        except Exception:
            return False

    def __le__(self, other: int) -> 'Size':
        return Size.__new__(Size, lambda x, y: x <= y, other)
    def __lt__(self, other: int) -> 'Size':
        return Size.__new__(Size, lambda x, y: x < y, other)
    def __ge__(self, other: int) -> 'Size':
        return Size.__new__(Size, lambda x, y: x >= y, other)
    def __gt__(self, other: int) -> 'Size':
        return Size.__new__(Size, lambda x, y: x > y, other)
    def __eq__(self, other: int) -> 'Size':
        return Size.__new__(Size, lambda x, y: x == y, other)
    def __ne__(self, other: int) -> 'Size':
        return Size.__new__(Size, lambda x, y: x != y, other)
