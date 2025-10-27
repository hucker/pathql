"""
Utility functions for PathQL actions.

Includes helpers for normalizing file path lists and (commented) query
matching utilities. Designed for use in file operations and filter logic.
All lines ≤88 chars for docstring compliance.
"""
from __future__ import annotations

import pathlib

from ..filters.alias import StrPathOrListOfStrPath


def normalize_file_str_list(file_list: StrPathOrListOfStrPath) -> list[pathlib.Path]:
    """Normalize list of paths given as str/Path, or list of str/Path into a flat list of Path objects."""
    if isinstance(file_list, str):
        return [pathlib.Path(file_list)]
    if isinstance(file_list, pathlib.Path):
        return [file_list]

    normalized_list: list[pathlib.Path] = []
    for item in file_list:
        normalized_list.append(pathlib.Path(item))

    return normalized_list

