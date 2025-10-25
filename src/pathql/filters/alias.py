"""Type aliases for the filters package.

Provides common TypeAlias names used throughout the filters module (e.g.
StatResultOrNone, DatetimeOrNone, IntOrFloat). Concrete filter class
imports are guarded under TYPE_CHECKING to avoid runtime circular imports;
add new numeric-comparison filter classes to NumericFilterType for accurate
static typing.
"""

from __future__ import annotations

import datetime as dt
import os
import pathlib
from typing import TYPE_CHECKING, Type, TypeAlias

if TYPE_CHECKING:
    # Imports only for static type checkers — avoid runtime circular imports
    from .age import AgeDays, AgeHours, AgeMinutes, AgeYears  # noqa: F401
    from .size import Size  # noqa: F401


# These filters support numeric comparisons (expressed as types of classes)
# Use explicit Type[...] union so static checkers see the concrete classes.
# Any Filters with numeric comparisons should be added here.
NumericFilterType: TypeAlias = (
    Type["Size"]
    | Type["AgeHours"]
    | Type["AgeMinutes"]
    | Type["AgeDays"]
    | Type["AgeYears"]
)

# Common type aliases used throughout PathQL to help static type checkers like mypy
StatResultOrNone: TypeAlias = os.stat_result | None
IntOrNone: TypeAlias = int | None
FloatOrNone: TypeAlias = float | None
DatetimeOrNone: TypeAlias = dt.datetime | None
PathOrNone: TypeAlias = pathlib.Path | None
IntOrFloatOrNone: TypeAlias = int | float | None
StrOrPath: TypeAlias = str | pathlib.Path
IntOrFloat: TypeAlias = int | float
StrOrListOfStr: TypeAlias = str | list[str]
StrPathOrListOfStrPath: TypeAlias = StrOrPath | list[StrOrPath]
