"""
FileDate filter for PathQL.

This module provides the FileDate class, which enables filtering files by their
modification, creation, access, or filename-encoded date. FileDate supports
operator overloading for direct comparison with datetime objects, allowing
expressive queries such as:

    FileDate().created > dt.datetime(2024, 1, 1)
    FileDate().modified <= dt.datetime(2024, 1, 1)
    FileDate().filename == dt.datetime(2024, 1, 1)

Use the .created, .modified, .accessed, or .filename properties for source selection.
"""

import datetime as dt
import operator
import pathlib
import datetime as dt
from typing import Any, Callable

from .alias import DatetimeOrNone, StatProxyOrNone
from .base import Filter
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
        self.source:str = source


    def _get_datetime(self, stat_proxy: StatProxyOrNone, path: pathlib.Path) -> dt.datetime:
        """
        Return the file's date according to the selected source.

        3 of the methods use the stat_proxy object to get the timestamps, while the file name
        method parses the date from the file name.
        """
        if self.source in ("modified", "created", "accessed"):
            if stat_proxy is None:
                raise ValueError(
                    f"FileDate filter requires stat_proxy for {self.source}, but none was provided."
                )
            st = stat_proxy.stat()
            if self.source == "modified":
                return dt.datetime.fromtimestamp(st.st_mtime)
            elif self.source == "created":
                return dt.datetime.fromtimestamp(st.st_ctime)
            elif self.source == "accessed":
                return dt.datetime.fromtimestamp(st.st_atime)
        elif self.source == "filename":
            # stat_proxy is not needed since the filename is in the filename
            # Example: expects YYYY-MM-DD in filename before an underscore
            return filename_to_datetime(path)

        raise ValueError(f"Unknown source for FileDate: `{self.source}`")


    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """
        FileDate itself is not a boolean filter. Use comparison operators to
        produce a Filter that implements .match(), e.g.:
            FileDate().modified < datetime.datetime(2024, 12, 1)
        """
        raise TypeError(
            "FileDate is not a boolean filter; use a comparison (e.g. "
            "FileDate().modified < datetime.datetime(...)) to obtain a Filter "
            "with a .match() method."
        )

    def _make_filter(self, op: Callable[[Any, Any], bool], other: dt.datetime):
        """
        Return a filter object with a .match() method that compares the file's date
        to 'other' using the operator 'op'.

        This enables operator overloading for comparison with datetime objects by creating
        the correct object for the comparison.
        """

        class DateComparisonFilter(Filter):
            def __init__(self, parent:Filter):
                self.parent = parent

            def match(
                self,
                path: pathlib.Path,
                stat_proxy: StatProxyOrNone = None,
                now: Any = None,
            ) -> bool:
                """Custom class where op is captured from outer scope."""
                #file_date = self.parent.match(path, stat_proxy=stat_proxy, now=now)
                file_date:dt.datetime = self.parent._get_datetime(stat_proxy, path)

                # Exception?
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
