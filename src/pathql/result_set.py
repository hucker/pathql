"""
This module provides the `ResultSet` class, which offers methods for aggregating
and analyzing collections of data. The class supports operations such as counting,
sorting, and retrieving statistical measures like median, average, minimum, and
maximum values.

Methods:
- `count`: Return the count of items in the result set.
- `sort_`: Sort the result set based on a key and order.
- `top_n`: Return the top N items from the result set.
- `bottom_n`: Return the bottom N items from the result set.
- `median`: Return the median value of the result set.
- `average`: Return the average value of the result set.
- `min`: Return the minimum value in the result set.
- `max`: Return the maximum value in the result set.

The `ResultSet` class is designed to work seamlessly with the PathQL query engine,
allowing users to perform complex queries and aggregations on file systems or other
data sources.
"""

import datetime as dt
import heapq
import pathlib
import statistics
from typing import Any, Callable, Optional

from .result_fields import ResultField

# scalar_aggregate is not used in this module; removed unused import


class ResultSet(list[pathlib.Path]):
    """
    A materialized list of pathlib.Path objects with aggregation and sorting methods.
    """

    def _get_key(self, field: ResultField) -> Callable[[pathlib.Path], Any]:
        """
        A materialized list of pathlib.Path objects with aggregation and sorting methods.
        """
        if field == ResultField.SIZE:
            return lambda f: f.stat().st_size
        elif field == ResultField.MTIME:
            return lambda f: f.stat().st_mtime
        elif field == ResultField.CTIME:
            return lambda f: f.stat().st_ctime
        elif field == ResultField.ATIME:
            return lambda f: f.stat().st_atime
        elif field == ResultField.MTIME_DT:
            return lambda f: dt.datetime.fromtimestamp(f.stat().st_mtime)
        elif field == ResultField.CTIME_DT:
            return lambda f: dt.datetime.fromtimestamp(f.stat().st_ctime)
        elif field == ResultField.ATIME_DT:
            return lambda f: dt.datetime.fromtimestamp(f.stat().st_atime)
        elif field == ResultField.NAME:
            return lambda f: f.name
        elif field == ResultField.SUFFIX:
            return lambda f: f.suffix
        elif field == ResultField.STEM:
            return lambda f: f.stem
        elif field == ResultField.PATH:
            return str  # lambda f: str(f)
        elif field == ResultField.PARENT:
            return lambda f: str(f.parent)
        elif field == ResultField.PARENTS:
            return lambda f: f.parent.parts
        elif field == ResultField.PARENTS_STEM_SUFFIX:
            return lambda f: (f.parent.parts, f.stem, f.suffix)
        else:
            raise ValueError(f"Unknown field: {field}")

    def max(self, field: ResultField) -> Optional[Any]:
        """Return the maximum value in the result set using built-in max."""
        key = self._get_key(field)
        vals = [key(f) for f in self]
        return max(vals) if vals else None

    def min(self, field: ResultField) -> Optional[Any]:
        """Return the minimum value in the result set using built-in min."""
        key = self._get_key(field)
        vals = [key(f) for f in self]
        return min(vals) if vals else None

    def average(self, field: ResultField) -> Optional[float]:
        """Return the average value of the result set using statistics.mean."""
        key = self._get_key(field)
        vals = [key(f) for f in self]
        return statistics.mean(vals) if vals else None

    def median(self, field: ResultField) -> Optional[float]:
        """Return the median value of the result set."""
        key = self._get_key(field)
        vals = [key(f) for f in self]
        return statistics.median(vals) if vals else None

    def count_(self) -> int:
        """Return the count of items in the result set."""
        return len(self)

    def sort_(self, field: ResultField, ascending: bool = True) -> "ResultSet":
        """Sort the result set based on a key and order."""
        key = self._get_key(field)
        return ResultSet(sorted(self, key=key, reverse=not ascending))

    def top_n(self, field: ResultField, n: int) -> "ResultSet":
        """Return the top N items from the result set."""
        key = self._get_key(field)
        return ResultSet(heapq.nlargest(n, self, key=key))

    def bottom_n(self, field: ResultField, n: int) -> "ResultSet":
        """Return the bottom N items from the result set."""
        key = self._get_key(field)
        return ResultSet(heapq.nsmallest(n, self, key=key))
 