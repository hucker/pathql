"""
Utility functions for PathQL actions.

Includes helpers for normalizing file path lists and (commented) query
matching utilities. Designed for use in file operations and filter logic.
All lines ≤88 chars for docstring compliance.
"""

from __future__ import annotations

import pathlib
from typing import Generator

from .filters.alias import StrPathOrListOfStrPath


def normalize_path(
    paths: StrPathOrListOfStrPath,
) -> Generator[pathlib.Path, None, None]:
    """
    Normalize input into a generator of pathlib.Path objects.
    Accepts a str, pathlib.Path, or a (possibly nested) list/tuple of those.
    Recursively flattens lists/tuples. Raises ValueError for unsupported types.
    All lines ≤88 chars for docstring compliance.
    """
    match paths:
        case str():
            yield pathlib.Path(paths)
        case pathlib.Path():
            yield paths
        case list() | tuple():
            for item in paths:
                yield from normalize_path(item)
        case _:
            raise ValueError(f"Invalid paths argument: {paths!r}")
