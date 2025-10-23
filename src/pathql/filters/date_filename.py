"""
Filename utilities for PathQL: generate archive names with sortable date/time prefixes.

The naming style ensures files are easily sorted by date and time, and provides an alternative way to group or filter files by temporal attributes.
Use these helpers to create consistent, sortable archive filenames for your workflows.
"""
import datetime as dt
import pathlib
import re
from dataclasses import dataclass
from typing import Optional

from .alias import IntOrNone, StrOrPath,DatetimeOrNone


@dataclass
class DateFilenameParts:
    """
    Represents the extracted date/time components from a filename.

    Fields are year, month, day, and hour. If a component is not present in the filename,
    its value will be None. Useful for grouping, filtering, or sorting files by temporal attributes.
    """

    year: int
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None


def filename_to_datetime_parts(filename: StrOrPath) -> DateFilenameParts|None:
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
        return None
    parts = match.groupdict()
    return DateFilenameParts(
        year=int(parts["year"]),
        month=int(parts["month"]) if parts["month"] else None,
        day=int(parts["day"]) if parts["day"] else None,
        hour=int(parts["hour"]) if parts["hour"] else None,
    )


def path_from_dt_ints(
    name: str,
    ext: str,
    year: int,  # year required
    month: IntOrNone = None,
    day: IntOrNone = None,
    hour: IntOrNone = None,
    dtp: DateFilenameParts | None = None,
) -> str:
    """
    Build a filename from explicit date parts.
    The width is inferred from which parts are provided.
    Raises ValueError if parts are inconsistent.
    """
    ext = ext.lstrip(".")
    ext_part = f".{ext}" if ext else ""
    if dtp is not None:
        year = dtp.year
        month = dtp.month
        day = dtp.day
        hour = dtp.hour

    parts:list[IntOrNone] = [year, month, day, hour]

    # Check contiguous prefix pattern: all values, then all Nones
    found_none = False
    for v in parts:
        if v is None:
            found_none = True
        elif found_none:
            raise ValueError("Invalid date string: date parts must be contiguous from the left (year, month, day, hour).")

    if hour is not None:
        return f"{year:04d}-{month:02d}-{day:02d}_{hour:02d}_{name}{ext_part}"
    elif day is not None:
        return f"{year:04d}-{month:02d}-{day:02d}_{name}{ext_part}"
    elif month is not None:
        return f"{year:04d}-{month:02d}_{name}{ext_part}"
    else:
        return f"{year}-{name}{ext_part}"

def path_from_datetime(
    name: str,
    ext: str,
    width: str,
    dt_: DatetimeOrNone,
) -> str:
    """
    Build a filename from a datetime object and a width ('year', 'month', 'day', 'hour').

    This is the recommended way to build a folder or file name from a date.
    """

    # Normalize width
    width = width.lower()

    # Allow default to now
    dt_ = dt_ or dt.datetime.now()

    if width == "year":
        return path_from_dt_ints(name, ext, dt_.year)
    elif width == "month":
        return path_from_dt_ints(name, ext, dt_.year, dt_.month)
    elif width == "day":
        return path_from_dt_ints(name, ext, dt_.year, dt_.month, dt_.day)
    elif width == "hour":
        return path_from_dt_ints(name, ext, dt_.year, dt_.month, dt_.day, dt_.hour)

    raise ValueError(f"Unhandled width '{width}'.")


def filename_to_datetime(filename: StrOrPath) -> dt.datetime:
    """
    Given a filename, extract its date components and return a datetime object.
    Year is required; missing month/day/hour are filled with 1/1/0 respectively.
    Raises ValueError if year is missing.

    NOTE: This function assumens that the file name is correctly formatted using
          YYYY-(MM)-(DD)_(HH) a leading date pattern in sortable ymdhms format.
          At this time this is the only supported format and for now is an
          opinionated design choice.
    """
    parts = filename_to_datetime_parts(filename)
    if parts is None or parts.year is None:
        raise ValueError("Year is required in filename to convert to datetime.")
    return dt.datetime(
        parts.year,
        parts.month if parts.month is not None else 1,
        parts.day if parts.day is not None else 1,
        parts.hour if parts.hour is not None else 0,
        0,  # minute
        0,  # second
    )
