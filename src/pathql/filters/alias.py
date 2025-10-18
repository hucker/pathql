"""Type aliases for PathQL."""

from typing import TypeAlias
import os
import datetime as dt
import pathlib


# Common type aliases used throughout PathQL to help static type checkers like mypy
StatResultOrNone: TypeAlias = os.stat_result | None
IntOrNone: TypeAlias = int | None
FloatOrNone: TypeAlias = float | None
DatetimeOrNone: TypeAlias = dt.datetime | None
PathOrNone: TypeAlias = pathlib.Path | None
IntOrFloatOrNone: TypeAlias = int | float | None
