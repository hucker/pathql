"""Top-level PathQL package exports and convenience imports."""

from .filters.age import AgeDays, AgeMinutes, AgeYears, AgeHours
from .filters.base import Filter
from .filters.datetime_parts import (
    DayFilter,
    HourFilter,
    MinuteFilter,
    MonthFilter,
    SecondFilter,
    YearFilter,
)
from .filters.file import File
from .filters.size import Size, parse_size
from .filters.stem import Name, Stem
from .filters.suffix import Ext, Suffix
from .filters.file_type import FileType
from .filters.fileage import (
    FilenameAgeHours,
    FilenameAgeDays,
    FilenameAgeYears,
)
from .query import Query

__version__ = "0.0.3"

__all__ = [
    "Filter",
    "Suffix",
    "Ext",
    "Size",
    "AgeMinutes",
    "AgeHours",
    "AgeDays",
    "AgeYears",
    "Stem",
    "Name",
    "FileType",
    "YearFilter",
    "MonthFilter",
    "DayFilter",
    "HourFilter",
    "MinuteFilter",
    "SecondFilter",
    "FilenameAgeHours",
    "FilenameAgeDays",
    "FilenameAgeYears",
    "File",
    "Query",
    "parse_size",
]
