"""Top-level PathQL package exports and convenience imports."""

from .filters.age import AgeDays, AgeHours, AgeMinutes, AgeYears
from .filters.alias import StatProxy, StatProxyOrNone
from .filters.base import Filter
from .filters.between import Between
from .filters.date_filename import filename_to_datetime
from .filters.datetime_parts import (
    DayFilter,
    HourFilter,
    MinuteFilter,
    MonthFilter,
    SecondFilter,
    YearFilter,
)
from .filters.file import File
from .filters.file_age import FilenameAgeDays, FilenameAgeHours, FilenameAgeYears
from .filters.file_type import FileType
from .filters.size import Size, parse_size
from .filters.stem import Stem
from .filters.suffix import Ext, Suffix
from .query import Query

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
    "filename_to_datetime",
]
