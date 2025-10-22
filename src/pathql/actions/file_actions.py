"""
File actions for pathql: generic batch operation on files.

Use `apply_action` to apply any function to each file, optionally with a target directory.
Public API: copy_files, move_files, delete_files.
"""

import pathlib
import shutil
from dataclasses import dataclass
from typing import Callable, Dict, List

EXCEPTIONS: tuple[type[Exception], ...] = (
    IOError,
    PermissionError,
    OSError,
    FileNotFoundError,
    NotADirectoryError,
)

@dataclass
class FileActionResult:
    """
    Represents the result of a batch file action (copy, move, delete).
    Contains lists of successful and failed files, and a mapping of errors.
    Properties:
        success: List of files that were processed successfully.
        failed: List of files that failed to process.
        errors: Mapping of files to exceptions raised during processing.
        status: True if all actions succeeded (no failures), else False.
    """
    success: List[pathlib.Path]
    failed: List[pathlib.Path]
    errors: Dict[pathlib.Path, Exception]

    @property
    def status(self) -> bool:
        """True if all actions succeeded (no failures)."""
        return not self.failed

def apply_action(
    files: list[pathlib.Path],
    action: Callable[[pathlib.Path, pathlib.Path | None], None],
    target_dir: pathlib.Path | None = None,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Apply an action to a list of files with error handling.
    Args:
        files: List of files to process.
        action: Function to apply to each file.
        target_dir: Optional target directory for the action.
        ignore_access_exception: If True, ignore access exceptions; otherwise, raise them.
        exceptions: Tuple of exception types to catch.
    Returns:
        FileActionResult: Object containing lists of successful, failed, and errored files.
    """
    result = FileActionResult(success=[], failed=[], errors={})
    if target_dir is not None:
        target_dir = pathlib.Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
    for p in files:
        try:
            action(p, target_dir)
            result.success.append(p)
        except exceptions as e:
            result.failed.append(p)
            result.errors[p] = e
            if not ignore_access_exception:
                raise
    return result

def combine_results(*results: FileActionResult) -> FileActionResult:
    """
    Combine multiple FileActionResult objects into one.
    Args:
        *results: Any number of FileActionResult objects.
    Returns:
        FileActionResult: Combined result with merged success, failed, and errors.
    """
    success: list[pathlib.Path] = []
    failed: list[pathlib.Path] = []
    errors: dict[pathlib.Path, Exception] = {}
    for r in results:
        success.extend(r.success)
        failed.extend(r.failed)
        errors.update(r.errors)
    return FileActionResult(success=success, failed=failed, errors=errors)

# Example actions:
def _copy_action(src: pathlib.Path, dest_dir: pathlib.Path | None) -> None:
    """Copy a source file to the destination directory."""
    if dest_dir is not None:
        shutil.copy2(str(src), str(dest_dir / src.name))

def _move_action(src: pathlib.Path, dest_dir: pathlib.Path | None) -> None:
    """Move a source file to the destination directory."""
    if dest_dir is not None:
        shutil.move(str(src), str(dest_dir / src.name))

def _delete_action(src: pathlib.Path, _: pathlib.Path | None) -> None:
    """Delete a source file."""
    src.unlink()

# Public API wrappers:
def copy_files(
    files: list[pathlib.Path],
    dest_dir: pathlib.Path,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Copy files to dest_dir.
    Args:
        files: List of files to copy.
        dest_dir: Destination directory for copied files.
        ignore_access_exception: If True, ignore access exceptions; otherwise, raise them.
        exceptions: Tuple of exception types to catch.
    Returns:
        FileActionResult: Object containing lists of successful, failed, and errored files.
    """
    return apply_action(
        files, _copy_action, dest_dir, ignore_access_exception, exceptions
    )

def move_files(
    files: list[pathlib.Path],
    dest_dir: pathlib.Path,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Move files to dest_dir.
    Args:
        files: List of files to move.
        dest_dir: Destination directory for moved files.
        ignore_access_exception: If True, ignore access exceptions; otherwise, raise them.
        exceptions: Tuple of exception types to catch.
    Returns:
        FileActionResult: Object containing lists of successful, failed, and errored files.
    """
    return apply_action(
        files, _move_action, dest_dir, ignore_access_exception, exceptions
    )

def delete_files(
    files: list[pathlib.Path],
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Delete files.
    Args:
        files: List of files to delete.
        ignore_access_exception: If True, ignore access exceptions; otherwise, raise them.
        exceptions: Tuple of exception types to catch.
    Returns:
        FileActionResult: Object containing lists of successful, failed, and errored files.
    """
    return apply_action(
        files, _delete_action, None, ignore_access_exception, exceptions
    )
