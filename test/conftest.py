import pytest
import sys
import os
import pathlib
import time
from typing import Dict
from typing import Dict


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
def size_test_folder(tmp_path):
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
def rich_filesystem(tmp_path):
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
