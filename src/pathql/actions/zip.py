"""Actions for creating zip archives from lists of Path objects."""

import pathlib
import zipfile

from ..filters.alias import StrPathOrListOfStrPath
from .file_actions import (
    EXCEPTIONS,
    FileActionResult,
    combine_results,
    copy_files,
    delete_files,
    move_files,
)
from ..utils import normalize_path


def _zip_apply_action(
    files: StrPathOrListOfStrPath,
    target_zip: pathlib.Path,
    preserve_dir_structure: bool = True,
    root: pathlib.Path | None = None,
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
    target_zip = pathlib.Path(target_zip) #allows str input
    target_zip.parent.mkdir(parents=True, exist_ok=True)
    compress_mode = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
    paths = normalize_path(files)

    if preserve_dir_structure:
        if root is None:
            root = pathlib.Path(".")
        elif isinstance(root,str):
            root = pathlib.Path(root)

    with zipfile.ZipFile(target_zip, "a", compression=compress_mode) as zf:
        for p in paths:
            if preserve_dir_structure:
                assert isinstance(root, pathlib.Path)
                try:
                    arcname = p.relative_to(root)
                except ValueError:
                    arcname = p.name
            else:
                arcname = p.name
            try:
                zf.write(p, arcname=str(arcname))
                result.success.append(p)
            except exceptions as e:
                result.failed.append(p)
                result.errors[p] = e
    return result


def zip_files(
    files: StrPathOrListOfStrPath,
    target_zip: pathlib.Path,
    preserve_dir_structure: bool = True,
    root: pathlib.Path | None = None,
    compress: bool = True,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Zip the provided files from root to target_zip.
    Each file's path in the archive is stored relative to `root` if
    `preserve_dir_structure` is True, preserving the directory structure
    under `root`. If False, only the file names are stored in the archive.
    Args:
        files: Files to zip.
        root: Base directory for relative paths in the archive.
        target_zip: Path to the zip archive.
        preserve_dir_structure: If True, store paths relative to root.
        compress: Use compression if True.
        exceptions: Exception types to catch.
    Returns:
        FileActionResult: Success, failed, and error details.
    """
    return _zip_apply_action(
        files,
        target_zip,
        preserve_dir_structure,
        root,
        compress,
        exceptions,
    )


def zip_delete_files(
    files: StrPathOrListOfStrPath,
    target_zip: pathlib.Path,
    preserve_dir_structure: bool = True,
    root: pathlib.Path | None = None,
    compress: bool = True,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Zip files, then delete them. Returns FileActionResult with combined results.
    Files are zipped using the same rules as zip_files: if
    `preserve_dir_structure` is True, paths are stored relative to `root`;
    otherwise, only file names are stored. After zipping, files are deleted.
    Args:
        files: Files to zip and delete.
        root: Base directory for relative paths in the archive.
        target_zip: Path to the zip archive.
        preserve_dir_structure: If True, store paths relative to root.
        compress: Use compression if True.
        ignore_access_exception: Ignore access errors if True.
        exceptions: Exception types to catch.
    Returns:
        FileActionResult: Combined results of zip and delete actions.
    """
    zip_result = zip_files(
        files,
        target_zip,
        preserve_dir_structure,
        root,
        compress,
        exceptions,
    )

    delete_result = delete_files(files, ignore_access_exception=ignore_access_exception)
    return combine_results(zip_result, delete_result)


def zip_move_files(
    files: StrPathOrListOfStrPath,
    target_zip: pathlib.Path,
    move_target: pathlib.Path,
    preserve_dir_structure: bool = True,
    root: pathlib.Path | None = None,
    compress: bool = True,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Zip files, then move them to move_target. Returns FileActionResult with combined results.
    Files are zipped using the same rules as zip_files: if
    `preserve_dir_structure` is True, paths are stored relative to `root`;
    otherwise, only file names are stored. After zipping, files are moved to
    move_target.
    Args:
        files: Files to zip and move.
        root: Base directory for relative paths in the archive.
        target_zip: Path to the zip archive.
        move_target: Directory to move files to after zipping.
        preserve_dir_structure: If True, store paths relative to root.
        compress: Use compression if True.
        ignore_access_exception: Ignore access errors if True.
        exceptions: Exception types to catch.
    Returns:
        FileActionResult: Combined results of zip and move actions.
    """
    zip_result = zip_files(
        files,
        target_zip,
        preserve_dir_structure,
        root,
        compress,
        exceptions,
    )
    move_result = move_files(
        files,
        move_target,
        ignore_access_exception=ignore_access_exception,
    )
    return combine_results(zip_result, move_result)


def zip_copy_files(
    files: StrPathOrListOfStrPath,
    target_zip: pathlib.Path,
    copy_target: pathlib.Path,
    preserve_dir_structure: bool = True,
    root: pathlib.Path | None = None,
    compress: bool = True,
    ignore_access_exception: bool = False,
    exceptions: tuple[type[Exception], ...] = EXCEPTIONS,
) -> FileActionResult:
    """
    Zip files, then copy them to copy_target. Returns FileActionResult with combined results.
    Files are zipped using the same rules as zip_files: if
    `preserve_dir_structure` is True, paths are stored relative to `root`;
    otherwise, only file names are stored. After zipping, files are copied to
    copy_target.
    Args:
        files: Files to zip and copy.
        root: Base directory for relative paths in the archive.
        target_zip: Path to the zip archive.
        copy_target: Directory to copy files to after zipping.
        preserve_dir_structure: If True, store paths relative to root.
        compress: Use compression if True.
        ignore_access_exception: Ignore access errors if True.
        exceptions: Exception types to catch.
    Returns:
        FileActionResult: Combined results of zip and copy actions.
    """
    zip_result = zip_files(
        files,
        target_zip,
        preserve_dir_structure,
        root,
        compress,
        exceptions,
    )
    copy_result = copy_files(
        files,
        copy_target,
        ignore_access_exception=ignore_access_exception,
    )
    return combine_results(zip_result, copy_result)
