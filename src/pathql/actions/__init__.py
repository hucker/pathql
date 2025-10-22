"""
Public API for pathql actions: file operations and zip utilities.
All functions operate on lists of pathlib.Path objects (or ResultSet).
"""

from .file_actions import (
    copy_files,
    delete_files,
    move_files,
    EXCEPTIONS,
    FileActionResult,
    combine_results,
)

from .zip import (
    zip_files,
    zip_delete_files,
    zip_move_files,
    zip_copy_files,
)

__all__ = [
    "copy_files",
    "delete_files",
    "move_files",
    "FileActionResult",
    "combine_results",
    "EXCEPTIONS",
    "zip_copy_files",
    "zip_delete_files",
    "zip_files",
    "zip_move_files",
]