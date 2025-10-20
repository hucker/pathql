from __future__ import annotations

import re
import pathlib
from typing import Callable, Mapping, Final, Pattern
from types import NotImplementedType
from .alias import StatResultOrNone, IntOrNone, DatetimeOrNone
from .base import Filter


# Accept ints, floats, or strings like "1.5 kb". Default to binary units (KB=1024).
_SIZE_RE: Final[Pattern[str]] = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([kmgtpe]?i?b?|b)?\s*$", re.IGNORECASE)
_UNIT_MULTIPLIERS: Final[Mapping[str, int]] = {
    "": 1,
    "b": 1,
    # SI (decimal) for plain suffixes
    "k": 1000,
    "kb": 1000,
    "m": 1000 ** 2,
    "mb": 1000 ** 2,
    "g": 1000 ** 3,
    "gb": 1000 ** 3,
    "t": 1000 ** 4,
    "tb": 1000 ** 4,
    "p": 1000 ** 5,
    "pb": 1000 ** 5,
    "e": 1000 ** 6,
    "eb": 1000 ** 6,
    # IEC (binary) for explicit "i" suffixes
    "kib": 1024,
    "mib": 1024 ** 2,
    "gib": 1024 ** 3,
    "tib": 1024 ** 4,
    "pib": 1024 ** 5,
    "eib": 1024 ** 6,
}


def _parse_size(value: object) -> int | NotImplementedType:
    """Parse int/float/string sizes into bytes (int).

    Returns:
      - int: parsed byte count
      - NotImplemented: if the operand type is not supported (so Python can
        attempt reflected operations)

    Raises:
      ValueError: for invalid numeric strings or negative values.
    """
    # direct ints/floats
    if isinstance(value, int):
        val = float(value)
    elif isinstance(value, float):
        val = value
    elif isinstance(value, str):
        m = _SIZE_RE.match(value)
        if not m:
            raise ValueError(f"invalid size string: {value!r}")
        num_str, unit = m.group(1), (m.group(2) or "").lower()
        try:
            num = float(num_str)
        except ValueError as exc:
            raise ValueError(f"invalid numeric value in size: {value!r}") from exc
        mult = _UNIT_MULTIPLIERS.get(unit)
        if mult is None:
            raise ValueError(f"unknown size unit: {unit!r}")
        val = num * mult
    else:
        return NotImplemented

    if val < 0:
        raise ValueError("size must be non-negative")

    return int(val)


def parse_size(value: object) -> int:
    """Public wrapper for size parsing.

    Accepts int, float, or string with units and returns an integer byte count.
    Raises ValueError for invalid numeric strings or negative values. Raises
    TypeError if the operand type is unsupported.
    """
    res = _parse_size(value)
    if res is NotImplemented:
        raise TypeError("unsupported operand type for parse_size")
    return res


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

    Notes:
    - Operator overloads accept ints, floats, and size strings (e.g. "1.5 kb").
    - For unsupported operand types the dunder returns NotImplemented so Python
      will attempt the reflected operation on the other operand. This is not
      an exception — invalid numeric values (e.g. negative sizes) raise
      ValueError.
    """
    def __init__(self, op: Callable[[int, int], bool] | None = None, value: IntOrNone = None) -> None:
        # op compares two integer byte counts
        self.op: Callable[[int, int], bool] | None = op
        self.value: IntOrNone = value
    def match(self, path: pathlib.Path, now: DatetimeOrNone = None, stat_result: StatResultOrNone = None) -> bool:
        if self.op is None or self.value is None:
            raise TypeError("Size filter not fully specified.")
        try:
            st = stat_result if stat_result is not None else path.stat()
            size: int = st.st_size
            return self.op(size, self.value)
        except (OSError, TypeError, ValueError):
            # stat can raise OSError; op may raise TypeError/ValueError for bad inputs.
            return False

    def __le__(self, other: object) -> Size | NotImplementedType:
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x <= y, parsed)

    def __lt__(self, other: object) -> Size | NotImplementedType:
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x < y, parsed)

    def __ge__(self, other: object) -> Size | NotImplementedType:
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x >= y, parsed)

    def __gt__(self, other: object) -> Size | NotImplementedType:
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x > y, parsed)

    def __eq__(self, other: object) -> Size | NotImplementedType:
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x == y, parsed)

    def __ne__(self, other: object) -> Size | NotImplementedType:
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x != y, parsed)
