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
from typing import Any, Callable

from .alias import StatProxyOrNone
from .attribute_filter import AttributeFilter
from .date_filename import filename_to_datetime


class FileDate(AttributeFilter):
    """
    Filter that extracts a file's date (from stat or filename) and allows comparison with a datetime.
    Supports operator overloading for >, >=, <, <=, ==, !=.
    Use .created, .modified, .accessed, or .filename properties for source selection.
    """

    def __init__(
        self,
        source: str = "modified",
        op: Callable[[Any, Any], bool] = None,
        value: dt.datetime = None,
    ):
        self.source = source

        def extractor(
            path: pathlib.Path, stat_proxy: StatProxyOrNone, now: Any = None
        ) -> dt.datetime:
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
                return filename_to_datetime(path)
            raise ValueError(f"Unknown source for FileDate: `{self.source}`")

        super().__init__(
            extractor, op, value, requires_stat=(self.source != "filename")
        )

    @property
    def accessed(self) -> "FileDate":
        return FileDate(source="accessed")

    @property
    def created(self) -> "FileDate":
        return FileDate(source="created")

    @property
    def modified(self) -> "FileDate":
        return FileDate(source="modified")

    @property
    def filename(self) -> "FileDate":
        return FileDate(source="filename")

    def __gt__(self, other: dt.datetime):
        return FileDate(self.source, operator.gt, other)

    def __ge__(self, other: dt.datetime):
        return FileDate(self.source, operator.ge, other)

    def __lt__(self, other: dt.datetime):
        return FileDate(self.source, operator.lt, other)

    def __le__(self, other: dt.datetime):
        return FileDate(self.source, operator.le, other)

    def __eq__(self, other: dt.datetime):
        return FileDate(self.source, operator.eq, other)

    def __ne__(self, other: dt.datetime):
        return FileDate(self.source, operator.ne, other)
