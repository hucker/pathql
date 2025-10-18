"""
conftest.py - Pytest fixtures for PathQL test suite.

This module provides reusable fixtures for testing PathQL's file query and filter logic, including:
- rwx access matrix files for permission-based filter tests
- size-based test folders for aggregation and sorting
- rich filesystem structures for recursive and symlink tests
- result set files with known sizes and names for aggregation and sorting validation

All fixtures use pytest's tmp_path for automatic cleanup and cross-platform compatibility.
"""
import sys
import os
import pathlib
import time
from typing import Dict

import pytest


def _set_permissions(path: pathlib.Path, readable: bool, writable: bool, executable: bool):
    if sys.platform == "win32":
        # On Windows, .exe extension for executable
        if executable:
            path = path.with_suffix(".exe")
            path.write_bytes(path.read_bytes())
        # Read/write: Windows doesn't use chmod, but we can try
        # Note: os.chmod may not work as expected on Windows
        mode = 0o666 if readable and writable else 0o444 if readable else 0o222 if writable else 0o000
        try:
            os.chmod(path, mode)
        except Exception:
            pass
    else:
        # Unix: set permissions using chmod
        mode = 0
        if readable:
            mode |= 0o400
        if writable:
            mode |= 0o200
        if executable:
            mode |= 0o100
        os.chmod(path, mode)
    return path

@pytest.fixture(scope="function")
def access_matrix(tmp_path: pathlib.Path) -> Dict[str, pathlib.Path]:
    """
    Creates all combinations of rwx files in tmp_path.
    Returns a dict mapping file name (e.g. 'rwx.ext') to pathlib.Path.
    """
    perms = [
        (True, True, True, "rwx"),
        (True, True, False, "rw"),
        (True, False, True, "rx"),
        (True, False, False, "r"),
        (False, True, True, "wx"),
        (False, True, False, "w"),
        (False, False, True, "x"),
        (False, False, False, "none"),
    ]
    files = {}
    for readable, writable, executable, base in perms:
        ext = ".exe" if executable and sys.platform == "win32" else ".ext"
        fname = f"{base}{ext}"
        fpath = tmp_path / fname
        fpath.write_bytes(b"test")
        fpath = _set_permissions(fpath, readable, writable, executable)
        files[fname] = fpath
    yield files
    for f in files.values():
        try:
            f.unlink()
        except Exception:
            pass

@pytest.fixture(scope="function")
def size_test_folder(tmp_path:pathlib.Path):
    """
    Create a folder with two files: 100.txt (100 bytes), 200.txt (200 bytes)
    """
    f1 = tmp_path / "100.txt"
    f2 = tmp_path / "200.txt"
    f1.write_bytes(b"A" * 100)
    f2.write_bytes(b"B" * 200)
    return tmp_path
## Removed unused/redundant imports

@pytest.fixture(scope="function")
def rich_filesystem(tmp_path:pathlib.Path):
    """
    Create a rich file system structure for testing:
    - root/
        - a10.txt (10 bytes)
        - b20.png (20 bytes)
        - c/
            - d30.txt (30 bytes)
            - e40.bmp (40 bytes)
            - f/
                - g50.txt (50 bytes)
                - h60.png (60 bytes)
        - i.link (symlink to a10.txt)
    Sets modification and creation times for control.
    """
    root = tmp_path
    files = [
        root / "a10.txt",
        root / "b20.png",
        root / "c" / "d30.txt",
        root / "c" / "d31.txt",
        root / "c" / "e40.bmp",
        root / "c" / "e41.bmp",
        root / "c" / "f" / "g50.txt",
        root / "c" / "f" / "g51.txt",
        root / "c" / "f" / "h60.png",
        root / "c" / "f" / "h61.png",
    ]
    (root / "c").mkdir(exist_ok=True)
    (root / "c" / "f").mkdir(exist_ok=True)
    # Write files
    for f in files:
        size = int(''.join(filter(str.isdigit, f.name)))
        f.write_bytes(b"X" * size)
    # Symlink (if supported)
    try:
        (root / "i.link").symlink_to(root / "a10.txt")
    except Exception:
        pass
    # Set times: age in seconds = file size
    now = time.time()
    for f in files:
        size = int(''.join(filter(str.isdigit, f.name)))
        os.utime(f, (now - size, now - size))
    return root, now


def _create_test_files(tmp_path: pathlib.Path, files: dict[str, int]):
    """
    Helper function to create files with specified sizes in the given folder.
    """
    for name, size in files.items():
        p = tmp_path / name
        p.write_bytes(b'x' * size)

@pytest.fixture
def test_result_files(tmp_path: pathlib.Path) -> list[pathlib.Path]:
    """
    Create files with known sizes and useful names for aggregation and sorting tests.
    Returns a list of file paths.
    """
    files = {
        "largest_1.txt": 3000,
        "largest_2.txt": 2000,
        "largest_3.txt": 1000,
        "smallest_1.txt": 10,
        "smallest_2.txt": 20,
        "smallest_3.txt": 30,
        "avg_1.txt": 100,
        "avg_2.txt": 200,
        "avg_3.txt": 300,
        "med_1.txt": 100,
        "med_2.txt": 200,
        "med_3.txt": 400,
        "a_first.txt": 150,
        "z_last.txt": 250,
        "middle.txt": 175,
    }
    _create_test_files(tmp_path, files)
    return [tmp_path / name for name in files.keys()]

@pytest.fixture
def test_result_folder(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Create files with known sizes and useful names for aggregation and sorting tests.
    Returns the folder containing the files.
    """
    files = {
        "largest_1.txt": 3000,
        "largest_2.txt": 2000,
        "largest_3.txt": 1000,
        "smallest_1.txt": 10,
        "smallest_2.txt": 20,
        "smallest_3.txt": 30,
        "avg_1.txt": 100,
        "avg_2.txt": 200,
        "avg_3.txt": 300,
        "med_1.txt": 100,
        "med_2.txt": 200,
        "med_3.txt": 400,
        "a_first.txt": 150,
        "z_last.txt": 250,
        "middle.txt": 175,
    }
    _create_test_files(tmp_path, files)
    return tmp_path

@pytest.fixture
def test_result_files_with_mtime(tmp_path: pathlib.Path) -> list[pathlib.Path]:
    """
    Create files named oldest_1.txt, oldest_2.txt, oldest_3.txt, middle_1.txt, ..., youngest_1.txt, youngest_2.txt, youngest_3.txt.
    Each file's modification time is set N days ago, for easy inspection and sorting by age.
    Returns a list of pathlib.Path objects.
    """
    files = [
        {"name": "oldest_1.txt", "size": 100, "modification_days_offset": 30},
        {"name": "oldest_2.txt", "size": 110, "modification_days_offset": 29},
        {"name": "oldest_3.txt", "size": 120, "modification_days_offset": 28},
        {"name": "middle_1.txt", "size": 130, "modification_days_offset": 15},
        {"name": "middle_2.txt", "size": 140, "modification_days_offset": 10},
        {"name": "middle_3.txt", "size": 150, "modification_days_offset": 5},
        {"name": "youngest_1.txt", "size": 160, "modification_days_offset": 2},
        {"name": "youngest_2.txt", "size": 170, "modification_days_offset": 1},
        {"name": "youngest_3.txt", "size": 180, "modification_days_offset": 0},
    ]
    paths: list[pathlib.Path] = []
    now = time.time()
    for file in files:
        p = tmp_path / file["name"]
        p.write_bytes(b'x' * file["size"])
        mtime = now - (file["modification_days_offset"] * 86400)
        os.utime(p, (mtime, mtime))
        paths.append(p)
    return paths