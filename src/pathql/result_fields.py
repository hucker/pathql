"""Enumerates fields that can be included in query results."""

from enum import Enum, auto


class ResultField(Enum):
    """Named result fields that can be projected in query output."""

    SIZE = auto()
    MTIME = auto()
    CTIME = auto()
    ATIME = auto()
    MTIME_DT = auto()
    CTIME_DT = auto()
    ATIME_DT = auto()
    NAME = auto()
    SUFFIX = auto()
    STEM = auto()
    PATH = auto()
    PARENT = auto()
    PARENTS = auto()
    PARENTS_STEM_SUFFIX = auto()
