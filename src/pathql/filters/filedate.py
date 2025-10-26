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

import datetime as dt
import operator
import pathlib
from typing import Any, Callable

from .base import Filter
from .alias import StatProxyOrNone,DatetimeOrNone
from .date_filename import filename_to_datetime

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
        self, path: pathlib.Path, stat_proxy: StatProxyOrNone = None, now: DatetimeOrNone = None,
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
                return dt.datetime.fromtimestamp(st.st_mtime)
            elif self.source == "created":
                return dt.datetime.fromtimestamp(st.st_ctime)
            elif self.source == "accessed":
                return dt.datetime.fromtimestamp(st.st_atime)
        elif self.source == "filename":
            # Example: expects YYYY-MM-DD in filename before an underscore
            return filename_to_datetime(path)
        else:
            return None

    def _make_filter(self, op: Callable[[Any, Any], bool], other: dt.datetime):
        """
        Return a filter object with a .match() method that compares the file's date
        to 'other' using the operator 'op'.

        This enables operator overloading for comparison with datetime objects by creating
        the correct object for the comparison.
        """

        class DateComparisonFilter(Filter):
            def __init__(self, parent):
                self.parent = parent

            def match(
                self,
                path: pathlib.Path,
                stat_proxy: StatProxyOrNone = None,
                now: Any = None,
            ) -> bool:
                """Custom class where op is captured from outer scope."""
                file_date = self.parent.match(path, stat_proxy=stat_proxy, now=now)
                if file_date is None:
                    return False
                return op(file_date, other)

        return DateComparisonFilter(self)

    @property
    def accessed(self) -> "FileDate":
        """Return a FileDate filter for file access time."""
        return FileDate().accessed # FileDate(source="accessed")

    @property
    def created(self) -> "FileDate":
        """Return a FileDate filter for file creation time."""
        return FileDate().created #  FileDate(source="created")

    @property
    def modified(self) -> "FileDate":
        """Return a FileDate filter for file modification time."""
        return FileDate().modified #(source="modified")

    @property
    def filename(self) -> "FileDate":
        """Return a FileDate filter for date parsed from filename."""
        return FileDate().filename #source="filename")

    # Operator overloads for comparison with datetime
    def __gt__(self, other: dt.datetime):
        return self._make_filter(operator.gt, other)

    def __ge__(self, other: dt.datetime):
        return self._make_filter(operator.ge, other)

    def __lt__(self, other: dt.datetime):
        return self._make_filter(operator.lt, other)

    def __le__(self, other: dt.datetime):
        return self._make_filter(operator.le, other)

    def __eq__(self, other: dt.datetime):
        return self._make_filter(operator.eq, other)

    def __ne__(self, other: dt.datetime):
        return self._make_filter(operator.ne, other)
