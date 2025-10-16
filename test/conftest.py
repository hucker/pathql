import pytest
import tempfile
import shutil
import os
import pathlib
import time

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
