"""
Test access filters using a full matrix of files with all combinations of read,
write, and execute permissions.

This module uses the access_matrix fixture (from conftest.py) to create files
named by their permissions (e.g., rwx.ext, r.ext, w.ext, etc.), sets permissions
cross-platform, and parameterizes tests to ensure each filter matches the correct
files.
"""

from pathlib import Path
import sys
from typing import Dict, List
import pytest
from pathql.filters import Read, Write, Execute, RdWt, RdWtEx, Filter



# Platform-specific expected filenames for each filter.
#
# On Windows, os.access only recognizes files as executable if they have a .exe extension.
# On Unix, executable files can have any extension, but permissions are set with chmod.
#
# These tables ensure the test matches the correct files for each platform.
expected_files_unix = {
    "Read": ["rwx.ext", "rw.ext", "rx.ext", "r.ext"],
    "Write": ["rwx.ext", "rw.ext", "wx.ext", "w.ext"],
    "Execute": ["rwx.ext", "rx.ext", "wx.ext", "x.ext"],
    "RdWt": ["rwx.ext", "rw.ext"],
    "RdWtEx": ["rwx.ext"],
}

expected_files_win = {
    "Read": ["rwx.exe", "rw.ext", "rx.exe", "r.ext"],
    "Write": ["rwx.exe", "rw.ext", "wx.exe", "w.ext"],
    "Execute": ["rwx.exe", "rx.exe", "wx.exe", "x.exe"],
    "RdWt": ["rwx.exe", "rw.ext"],
    "RdWtEx": ["rwx.exe"],
}

# Select the correct table for the current platform
table = expected_files_win if sys.platform == "win32" else expected_files_unix

@pytest.mark.parametrize(
    "filter_obj,expected_files",
    [
        (Read(), table["Read"]),
        (Write(), table["Write"]),
        (Execute(), table["Execute"]),
        (RdWt(), table["RdWt"]),
        (RdWtEx(), table["RdWtEx"]),
    ]
)
def test_access_matrix(
    access_matrix: Dict[str, Path], filter_obj: Filter, expected_files: List[str]
):
    """
    For each filter, check that only the expected files are matched.
    """
    matched = {fname for fname, fpath in access_matrix.items() if filter_obj.match(fpath)}
    expected = set(expected_files)
    assert matched == expected
