"""Top-level PathQL package exports and convenience imports."""

from .filters.age import AgeDays, AgeMinutes, AgeYears, AgeHours
from .filters.base import Filter
from .filters.between import Between
from .filters.alias import StatProxyOrNone,StatProxy
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
from .filters.stem import Stem
from .filters.suffix import Ext, Suffix
from .filters.file_type import FileType

from .filters.file_age import (
    FilenameAgeHours,
    FilenameAgeDays,
    FilenameAgeYears,
)
from .query import Query
from .filters.date_filename import filename_to_datetime

__version__ = "0.0.4"

__all__ = [
    "Between",
    "Filter",
    "Suffix",
    "Ext",
    "Size",
    "AgeMinutes",
    "AgeHours",
    "AgeDays",
    "AgeYears",
    "Stem",
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
    "StatProxyOrNone",
    "StatProxy",
    "filename_to_datetime"
]
