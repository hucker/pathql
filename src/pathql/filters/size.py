from __future__ import annotations

"""Utilities and a filter for parsing and matching file sizes."""
import pathlib
import re
from types import NotImplementedType
from typing import Callable, Final, Mapping, Pattern

from pathql.filters.stat_proxy import StatProxy

from .alias import DatetimeOrNone, IntOrNone
from .base import Filter

# Accept ints, floats, or strings like "1.5 kb". Default to binary units (KB=1024).
_SIZE_RE_STRING = r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([kmgtpe]?i?b?|b)?\s*$"
_SIZE_RE: Final[Pattern[str]] = re.compile(_SIZE_RE_STRING, re.IGNORECASE)


# Table lookup for multiplier strings -> multiplier.
_UNIT_MULTIPLIERS: Final[Mapping[str, int]] = {
    "": 1,
    "b": 1,
    # SI (decimal) for plain suffixes
    "k": 1000,
    "kb": 1000,
    "m": 1000**2,
    "mb": 1000**2,
    "g": 1000**3,
    "gb": 1000**3,
    "t": 1000**4,
    "tb": 1000**4,
    "p": 1000**5,
    "pb": 1000**5,
    "e": 1000**6,
    "eb": 1000**6,
    "zb": 1000**9,
    # IEC (binary) for explicit "i" suffixes
    "kib": 1024,
    "mib": 1024**2,
    "gib": 1024**3,
    "tib": 1024**4,
    "pib": 1024**5,
    "eib": 1024**6,
    "zib": 1024**9,
}


def _parse_size(value: object) -> int | NotImplementedType:
    """Parse int/float/string sizes into bytes.

    Returns NotImplemented for unsupported operand types so Python can try
    the reflected operation.
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
        multiplier = _UNIT_MULTIPLIERS.get(unit)
        if multiplier is None:
            raise ValueError(f"unknown size unit: {unit!r}")
        val = num * multiplier
    else:
        return NotImplemented

    if val < 0:
        raise ValueError("size must be non-negative")

    return int(val)


def parse_size(value: object) -> int:
    """Parse a size value and return the byte count as an int.

    Raises TypeError for unsupported operand types.
    """
    res = _parse_size(value)
    if res is NotImplemented:
        raise TypeError("unsupported operand type for parse_size")
    return res


class Size(Filter):
    """Filter for file size (in bytes)."""

    # This class requires stat data to function

    def __init__(
        self,
        op: Callable[[int, int], bool] | None = None,
        value: IntOrNone = None,
    ) -> None:
        """Initialize a Size filter.

        The op callable receives two integer byte counts.
        """
        self.op: Callable[[int, int], bool] | None = op
        self.value: IntOrNone = value

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxy | None = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """Return True if the file's size matches the filter criteria."""
        if self.op is None or self.value is None:
            raise TypeError("Size filter not fully specified.")
        if stat_proxy is None:
            raise ValueError("Size filter requires stat_proxy, but none was provided.")
        try:
            st = stat_proxy.stat()
            size: int = st.st_size
            return self.op(size, self.value)
        except (OSError, TypeError, ValueError):
            # stat can raise OSError; op may raise TypeError/ValueError for bad inputs.
            return False

    def __le__(self, other: object) -> Size | NotImplementedType:
        """Return a Size filter for <= comparison with size strings/ints."""
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x <= y, parsed)

    def __lt__(self, other: object) -> Size | NotImplementedType:
        """Return a Size filter for < comparison with size strings/ints."""
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x < y, parsed)

    def __ge__(self, other: object) -> Size | NotImplementedType:
        """Return a Size filter for >= comparison with size strings/ints."""
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x >= y, parsed)

    def __gt__(self, other: object) -> Size | NotImplementedType:
        """Return a Size filter for > comparison with size strings/ints."""
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x > y, parsed)

    def __eq__(self, other: object) -> Size | NotImplementedType:
        """Return a Size filter for == comparison with size strings/ints."""
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x == y, parsed)

    def __ne__(self, other: object) -> Size | NotImplementedType:
        """Return a Size filter for != comparison with size strings/ints."""
        parsed = _parse_size(other)
        if parsed is NotImplemented:
            return NotImplemented
        return Size(lambda x, y: x != y, parsed)
        return Size(lambda x, y: x != y, parsed)
