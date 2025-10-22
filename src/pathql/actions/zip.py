"""Actions for creating zip archives from lists of Path objects."""

import pathlib
import zipfile

from .file_actions import (
    EXCEPTIONS,
    FileActionResult,
    combine_results,
    copy_files,
    delete_files,
    move_files,
)

def zip_apply_action(
    files: list[pathlib.Path],
    root: pathlib.Path,
    target_zip: pathlib.Path,
    preserve_dir_structure: bool = True,
    compress: bool = True,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Apply zip operation to a list of files with error handling.
    Args:
        files: List of files to zip.
        root: Root directory for relative paths.
        target_zip: Path to the zip archive.
        preserve_dir_structure: Whether to preserve directory structure in archive.
        compress: Whether to use compression.
        exceptions: Tuple of exception types to catch.
    Returns:
        FileActionResult: Object containing lists of successful, failed, and errored files.
    """
    result = FileActionResult(success=[], failed=[], errors={})
    target_zip.parent.mkdir(parents=True, exist_ok=True)
    compress_mode = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
    with zipfile.ZipFile(target_zip, "a", compression=compress_mode) as zf:
        for p in files:
            try:
                arcname = p.relative_to(root) if preserve_dir_structure else p.name
            except ValueError:
                arcname = p.name
            try:
                zf.write(p, arcname=str(arcname))
                result.success.append(p)
            except exceptions as e:
                result.failed.append(p)
                result.errors[p] = e
    return result

def zip_files(
    files: list[pathlib.Path],
    root: pathlib.Path,
    target_zip: pathlib.Path,
    preserve_dir_structure: bool = True,
    compress: bool = True,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """Zip the provided files from root to target_zip. Returns FileActionResult."""
    return zip_apply_action(
        files, root, target_zip, preserve_dir_structure, compress, exceptions
    )

def zip_delete_files(
    files: list[pathlib.Path],
    root: pathlib.Path,
    target_zip: pathlib.Path,
    preserve_dir_structure: bool = True,
    compress: bool = True,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """Zip files, then delete them. Returns FileActionResult with combined results."""
    zip_result = zip_files(
        files, root, target_zip, preserve_dir_structure, compress, exceptions
    )
    delete_result = delete_files(
        root, files, ignore_access_exception=ignore_access_exception
    )
    return combine_results(zip_result, delete_result)

def zip_move_files(
    files: list[pathlib.Path],
    root: pathlib.Path,
    target_zip: pathlib.Path,
    move_target: pathlib.Path,
    preserve_dir_structure: bool = True,
    compress: bool = True,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """Zip files, then move them to move_target. Returns FileActionResult with combined results."""
    zip_result = zip_files(
        files, root, target_zip, preserve_dir_structure, compress, exceptions
    )
    move_result = move_files(
        root, files, move_target, ignore_access_exception=ignore_access_exception
    )
    return combine_results(zip_result, move_result)

def zip_copy_files(
    files: list[pathlib.Path],
    root: pathlib.Path,
    target_zip: pathlib.Path,
    copy_target: pathlib.Path,
    preserve_dir_structure: bool = True,
    compress: bool = True,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """Zip files, then copy them to copy_target. Returns FileActionResult with combined results."""
    zip_result = zip_files(
        files, root, target_zip, preserve_dir_structure, compress, exceptions
    )
    copy_result = copy_files(
        root, files, copy_target, ignore_access_exception=ignore_access_exception
    )
    return combine_results(zip_result, copy_result)