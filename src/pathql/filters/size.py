import pathlib
from typing import Callable, Type, Any

from .alias import StatResultOrNone, IntOrNone
from .base import Filter


class FilterMeta(type):
    """
    Metaclass for filter classes that enables declarative operator overloads.

    This allows expressions like `Size <= 1024` to return a new filter instance
    that matches files with size less than or equal to 1024 bytes, instead of
    returning a boolean. Each operator method constructs a filter with the
    appropriate comparison logic.

    Returns:
        A new filter instance (e.g., Size) configured with the specified operator and value.
    """
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
    def __init__(self, op: Callable[[Any, Any], bool], value: IntOrNone = None) -> None:
        """
        Initialize a Size filter.

        Args:
            op (callable, optional): Operator function (e.g., operator.le, operator.gt).
            value (int, optional): Value to compare file size against.
        """
        self.op: Callable[[Any, Any], bool]  = op
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

    def match(self, path: pathlib.Path, now=None, stat_result: StatResultOrNone = None) -> bool:
        """
        Determine if the file's size matches the filter criteria.

        Args:
            path: The pathlib.Path to check.
            now: (Unused, for API compatibility)
            stat_result: Optional os.stat_result for file metadata.

        Returns:
            bool: True if the file matches the size filter, False otherwise.
        """
        if self.op is None or self.value is None:
            raise ValueError("Size filter not fully specified.")
        try:
            st = stat_result if stat_result is not None else path.stat()
            size: int = st.st_size
            return self.op(size, self.value)
        except Exception:
            return False
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
