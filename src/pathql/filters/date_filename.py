"""
Filename utilities for PathQL: generate archive names with sortable date/time prefixes.

The naming style ensures files are easily sorted by date and time, and provides an alternative way to group or filter files by temporal attributes.
Use these helpers to create consistent, sortable archive filenames for your workflows.
"""

import datetime
import pathlib
import re
from dataclasses import dataclass
from typing import Optional

from .alias import IntOrNone, StrOrPath


@dataclass
class DateFilenameParts:
    """
    Represents the extracted date/time components from a filename.

    Fields are year, month, day, and hour. If a component is not present in the filename,
    its value will be None. Useful for grouping, filtering, or sorting files by temporal attributes.
    """
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None

def extract_date_filename_parts(filename: StrOrPath) -> DateFilenameParts:
    """
    Extracts yyyy, mm, dd, hh components from a filename of the form:
    YYYY-MM-DD_HH_{ArchiveName}.{EXT}, YYYY-MM-DD_{ArchiveName}.{EXT},
    YYYY-MM_{ArchiveName}.{EXT}, or YYYY-{ArchiveName}.{EXT}.
    Accepts a string or pathlib.Path; if pathlib.Path, uses the name attribute.
    Returns a DateFilenameParts dataclass with missing values as None.
    """
    if isinstance(filename, pathlib.Path):
        filename = filename.name
    # Regex explanation:
    # ^                   : Start of string
    # (?P<year>\d{4})     : 4-digit year, captured as 'year'
    # (?:-(?P<month>\d{2})): Optional 2-digit month, preceded by '-', captured as 'month'
    # (?:-(?P<day>\d{2})) : Optional 2-digit day, preceded by '-', captured as 'day'
    # (?:_(?P<hour>\d{2})): Optional 2-digit hour, preceded by '_', captured as 'hour'
    # [_-]                : Require either '_' or '-' after the date part to separate from archive name
    pattern = (
        r"^(?P<year>\d{4})"
        r"(?:-(?P<month>\d{2}))?"
        r"(?:-(?P<day>\d{2}))?"
        r"(?:_(?P<hour>\d{2}))?"
        r"[_-]"
    )
    match = re.match(pattern, filename)
    if not match:
        return DateFilenameParts()
    parts = match.groupdict()
    return DateFilenameParts(
        year=int(parts["year"]) if parts["year"] else None,
        month=int(parts["month"]) if parts["month"] else None,
        day=int(parts["day"]) if parts["day"] else None,
        hour=int(parts["hour"]) if parts["hour"] else None,
    )



def y_filename(name: str, ext: str, year: IntOrNone = None, now_: datetime.datetime | None = None) -> str:
    """
    y_filename generates a filename in the format YYYY-{ArchiveName}.{EXT}.

    If year is provided, it is used; otherwise, the year is taken from now_ or the current time.
    """
    if year is None:
        now_ = now_ or datetime.datetime.now()
        year = now_.year
    return f"{year}-{name}.{ext}"

def ym_filename(name: str, ext: str, year: IntOrNone = None, now_: datetime.datetime | None = None) -> str:
    """
    ym_filename generates a filename in the format YYYY-MM_{ArchiveName}.{EXT}.

    If year is provided, it is used; otherwise, the year and month are taken from now_ or the current time.
    """
    if year is None:
        now_ = now_ or datetime.datetime.now()
        year = now_.year
        month = now_.month
    else:
        now_ = now_ or datetime.datetime.now()
        month = now_.month
    return f"{year:04d}-{month:02d}_{name}.{ext}"


def ymdh_filename(
    name: str,
    ext: str = "",
    date_width: str = "year",  # "year", "month", "day", "hour"
    year: IntOrNone = None,
    month: IntOrNone = None,
    day: IntOrNone = None,
    hour: IntOrNone = None,
    now_: datetime.datetime | None = None
) -> str:
    """
    Generate a sortable filename with date prefix.
    If now_ is provided, manual date components are not allowed.
    If any manual date component is provided, all required for date_width must be present.
    Extension normalization is lenient: "txt" or ".txt" both work.
    """
    ext = ext.lstrip(".")
    ext_part = f".{ext}" if ext else ""

    required = {
        "year": ["year"],
        "month": ["year", "month"],
        "day": ["year", "month", "day"],
        "hour": ["year", "month", "day", "hour"],
    }
    if date_width not in required:
        raise ValueError(f"Invalid date_width '{date_width}'.")

    manual = [year, month, day, hour]
    if now_ is not None and any(x is not None for x in manual):
        raise ValueError("If now_ is provided, do not provide year/month/day/hour manually.")

    # If any manual date component is provided, all required for date_width must be provided
    if any(x is not None for x in manual):
        for field in required[date_width]:
            if locals()[field] is None:
                raise ValueError(f"{field.capitalize()} must be provided for date_width '{date_width}' when using manual date components.")
    else:
        # Fill values from now_ or current time
        dt = now_ or datetime.datetime.now()
        year, month, day, hour = dt.year, dt.month, dt.day, dt.hour

    # Build filename
    if date_width == "year":
        return f"{year}-{name}{ext_part}"
    elif date_width == "month":
        return f"{year:04d}-{month:02d}_{name}{ext_part}"
    elif date_width == "day":
        return f"{year:04d}-{month:02d}-{day:02d}_{name}{ext_part}"
    elif date_width == "hour":
        return f"{year:04d}-{month:02d}-{day:02d}_{hour:02d}_{name}{ext_part}"
