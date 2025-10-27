"""
AttributeFilter base class for PathQL filters.

Provides a generic filter for extracting file attributes and comparing them
to a threshold using a specified operator. Designed for subclassing by
filters like Age, Size, and FileDate. Supports stat-based and stat-less
extraction and robust error handling.
"""

import pathlib
from typing import Any, Callable

from .alias import StatProxyOrNone
from .base import Filter


class AttributeFilter(Filter):
    """
    Generic filter for extracting an attribute and comparing it.

    This class is a flexible base for filters that extract a value from a file
    (using a custom extractor) and compare it to a threshold using a specified
    operator. It supports stat-based and stat-less extraction, robust error
    handling, and is designed for subclassing by specific attribute filters
    (e.g., Age, Size, FileDate).

    Enables usage:
        Size() < 1024
        AgeDays() >= 30

    Args:
        extractor: Callable that extracts the attribute from a file
            (path, stat_proxy, now) -> value.
        op: Comparison operator (e.g., operator.lt, operator.ge) to apply to
            the extracted value and threshold.
        value: The threshold value to compare against.
        requires_stat: If True, raises ValueError if stat_proxy is not provided.
    """

    def __init__(
        self,
        extractor: Callable[[pathlib.Path, StatProxyOrNone, Any], Any],
        op: Callable[[Any, Any], bool],
        value: Any,
        requires_stat: bool = True,
    ):
        """
        Initialize an AttributeFilter.

        Args:
            extractor: Function to extract the attribute from the file.
            op: Comparison operator to apply.
            value: Threshold value for comparison.
            requires_stat: Whether stat_proxy is required for extraction.
        """
        self.extractor = extractor
        self.op = op
        self.value = value
        self.requires_stat = requires_stat

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: Any = None,
    ) -> bool:
        """
        Evaluate the filter against a file.

        Args:
            path: Path to the file being tested.
            stat_proxy: Optional stat proxy for file metadata extraction.
            now: Optional current time or context for extraction.

        Returns:
            True if the extracted attribute matches the comparison, False
            otherwise.

        Raises:
            TypeError: If the filter is not fully specified (missing operator
                or value).
            ValueError: If stat_proxy is required but not provided.
        """
        if self.op is None or self.value is None:
            raise TypeError(f"{self.__class__.__name__} filter not fully specified.")
        if self.requires_stat and stat_proxy is None:
            raise ValueError(
                f"{self.__class__.__name__} filter requires stat_proxy, but none was provided."
            )
        try:
            attr = self.extractor(path, stat_proxy, now)
            return self.op(attr, self.value)
        except Exception:
            return False
