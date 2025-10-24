from pathql.filters.stat_proxy import StatProxy

"""
FileDate filter for PathQL.

This module provides the FileDate class, which enables filtering files by their
modification, creation, access, or filename-encoded date. FileDate supports
operator overloading for direct comparison with datetime objects, allowing
expressive queries such as:

    FileDate().created > datetime.datetime(2024, 1, 1)
    FileDate().modified <= datetime.datetime(2024, 1, 1)
    FileDate().filename == datetime.datetime(2024, 1, 1)

Use the .created, .modified, .accessed, or .filename properties for source selection.
"""

import datetime
import operator
import pathlib
from typing import Any, Callable

from pathql.filters.base import Filter


class FileDate(Filter):
    """
    Filter that extracts a file's date (from stat or filename) and allows comparison with a datetime.
    Supports operator overloading for >, >=, <, <=, ==, !=.
    Use .created, .modified, .accessed, or .filename properties for source selection.
    """

    def __init__(self, source: str = "modified"):
        """
        Args:
            source: 'modified', 'created', 'accessed', or 'filename'.
                   Prefer using the .created, .modified, .accessed, or .filename properties.
        """
        self.source = source

    def match(
        self, path: pathlib.Path, stat_proxy: StatProxy | None = None, now: Any = None
    ) -> datetime.datetime | None:
        """
        Return the file's date according to the selected source.
        """
        if self.source in ("modified", "created", "accessed"):
            if stat_proxy is None:
                raise ValueError(
                    "FileDate filter requires stat_proxy, but none was provided."
                )
            st = stat_proxy.stat()
            if self.source == "modified":
                return datetime.datetime.fromtimestamp(st.st_mtime)
            elif self.source == "created":
                return datetime.datetime.fromtimestamp(st.st_ctime)
            elif self.source == "accessed":
                return datetime.datetime.fromtimestamp(st.st_atime)
        elif self.source == "filename":
            # Example: expects YYYY-MM-DD in filename before an underscore
            try:
                stem = path.stem
                date_str = stem.split("_")[0]
                return datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                return None
        else:
            return None

    def _make_filter(self, op: Callable[[Any, Any], bool], other: datetime.datetime):
        """
        Return a filter object with a .match() method that compares the file's date
        to 'other' using the operator 'op'.
        """

        class DateComparisonFilter(Filter):
            def __init__(self, parent):
                self.parent = parent

            def match(
                self,
                path: pathlib.Path,
                stat_proxy: StatProxy | None = None,
                now: Any = None,
            ) -> bool:
                file_date = self.parent.match(path, stat_proxy=stat_proxy, now=now)
                if file_date is None:
                    return False
                return op(file_date, other)

        return DateComparisonFilter(self)

    @property
    def accessed(self) -> "FileDate":
        """Return a FileDate filter for file access time."""
        return FileDate(source="accessed")

    @property
    def created(self) -> "FileDate":
        """Return a FileDate filter for file creation time."""
        return FileDate(source="created")

    @property
    def modified(self) -> "FileDate":
        """Return a FileDate filter for file modification time."""
        return FileDate(source="modified")

    @property
    def filename(self) -> "FileDate":
        """Return a FileDate filter for date parsed from filename."""
        return FileDate(source="filename")

    # Operator overloads for comparison with datetime
    def __gt__(self, other: datetime.datetime):
        return self._make_filter(operator.gt, other)

    def __ge__(self, other: datetime.datetime):
        return self._make_filter(operator.ge, other)

    def __lt__(self, other: datetime.datetime):
        return self._make_filter(operator.lt, other)

    def __le__(self, other: datetime.datetime):
        return self._make_filter(operator.le, other)

    def __eq__(self, other: datetime.datetime):
        return self._make_filter(operator.eq, other)

    def __ne__(self, other: datetime.datetime):
        return self._make_filter(operator.ne, other)
        return self._make_filter(operator.ne, other)
