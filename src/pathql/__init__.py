"""Top-level PathQL package exports and convenience imports."""

from .actions.file_actions import FileActionResult
from .actions.zip import zip_copy_files, zip_delete_files, zip_files, zip_move_files
from .filters.age import AgeDays, AgeHours, AgeMinutes, AgeYears
from .filters.alias import StatProxy, StatProxyOrNone
from .filters.base import (
    All,
    AllowAll,
    AllowNone,
    AndFilter,
    Filter,
    NotFilter,
    OrFilter,
)
from .filters.between import Between
from .filters.date_filename import (
    DateFilenameParts,
    filename_to_datetime,
    path_from_datetime,
    path_from_dt_ints,
)
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
from .filters.filedate import FileDate
from .filters.size import Size, parse_size
from .filters.stem import Stem
from .filters.suffix import Suffix
from .query import Query
from .result_fields import ResultField
from .result_set import ResultSet
from .utils import normalize_path

__version__ = "0.0.9"

__all__ = [
    "AgeDays",
    "AgeHours",
    "AgeMinutes",
    "AgeYears",
    "All",
    "AllowAll",
    "AllowNone",
    "AndFilter",
    "Between",
    "DateFilenameParts",
    "DayFilter",
    "File",
    "FileActionResult",
    "FileDate",
    "FileType",
    "FilenameAgeDays",
    "FilenameAgeHours",
    "FilenameAgeYears",
    "Filter",
    "HourFilter",
    "MinuteFilter",
    "MonthFilter",
    "NotFilter",
    "OrFilter",
    "parse_size",
    "path_from_datetime",
    "path_from_dt_ints",
    "Query",
    "ResultField",
    "ResultSet",
    "SecondFilter",
    "Size",
    "StatProxy",
    "StatProxyOrNone",
    "Stem",
    "Suffix",
    "YearFilter",
    "zip_copy_files",
    "zip_delete_files",
    "zip_files",
    "zip_move_files",
    "filename_to_datetime",
    "path_from_datetime",
    "normalize_path",
    "path_from_dt_ints",
]
