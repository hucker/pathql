"""Tests for Type filter, covering file, directory, and symlink detection."""

import pytest
import sys
from pathql.filters.type import Type

def test_type_file(tmp_path):
    """Test that Type.FILE matches a regular file."""
    f = tmp_path / "a.txt"
    f.write_text("A")
    assert (Type == Type.FILE).match(f)

def test_type_directory(tmp_path):
    """Test that Type.DIRECTORY matches a directory."""
    d = tmp_path / "dir"
    d.mkdir()
    assert (Type == Type.DIRECTORY).match(d)

def test_type_link(tmp_path):
    """
    Test that Type.LINK matches a symlink and not file or directory.
    WARNING: Symlink handling is platform-dependent and not well tested across all OSes and edge cases.
    """
    if sys.platform.startswith("win"):
        pytest.skip("Symlink tests are skipped on Windows.")
    f = tmp_path / "foo.txt"
    f.write_text("hello")
    link = tmp_path / "foo_link.txt"

    link.symlink_to(f)
    assert (Type == Type.LINK).match(link)
    assert not (Type == Type.FILE).match(link)

def test_type_union_and_set(tmp_path):
    """Test Type filter with set union and direct string/set construction."""
    f = tmp_path / "a.txt"
    f.write_text("A")
    d = tmp_path / "adir"
    d.mkdir()
    # Union using set of string constants
    type_union = {Type.FILE, Type.DIRECTORY}
    assert (Type == type_union).match(f)
    assert (Type == type_union).match(d)
    # Direct string
    assert Type("file").match(f)
    assert Type("directory").match(d)
    # Direct set
    assert Type({"file", "directory"}).match(f)
    assert Type({"file", "directory"}).match(d)
    # Union using set
    assert (Type == {Type.FILE, Type.DIRECTORY}).match(f)
    assert (Type == {Type.FILE, Type.DIRECTORY}).match(d)
    # Direct string
    assert Type("file").match(f)
    assert Type("directory").match(d)
    # Direct set
    assert Type({"file", "directory"}).match(f)
    assert Type({"file", "directory"}).match(d)

def test_type_contains():
    """Test __contains__ for Type filter set membership."""
    t = Type({Type.FILE, Type.DIRECTORY})
    assert Type.FILE in t
    assert Type.DIRECTORY in t
    assert Type.LINK not in t

def test_type_or_and_ror():
    """Test __or__ and __ror__ operator overloads for Type filter."""
    t1 = Type(Type.FILE)
    t2 = Type(Type.DIRECTORY)
    t3 = t1 | t2
    t4 = t2.__ror__(t1)
    assert Type.FILE in t3.type_names and Type.DIRECTORY in t3.type_names
    assert t3.type_names == t4.type_names

def test_type_error_handling(monkeypatch, tmp_path):
    """
    Test error handling and UNKNOWN logic in Type filter.
    WARNING: Symlink and broken symlink handling is platform-dependent and not well tested across all OSes and edge cases.
    """
    f = tmp_path / "err.txt"
    f.write_text("E")
    class BadPath(type(f)):
        def exists(self):
            return True
        def lstat(self):
            raise OSError("fail")
    bad = BadPath(f)
    # Should return True if UNKNOWN is in type_names, else False
    assert Type(Type.UNKNOWN).match(bad)
    assert not Type(Type.FILE).match(bad)
    if sys.platform.startswith("win"):
        pytest.skip("Symlink tests are skipped on Windows.")
    # On Windows, device files are rare, so test a broken symlink
    broken = tmp_path / "broken_link"
    broken.symlink_to(tmp_path / "does_not_exist.txt")
    # Should be LINK, not UNKNOWN, even if target missing
    assert (Type == Type.LINK).match(broken)
    # UNKNOWN only matches if not file, dir, or link
    # Create a path that doesn't exist and isn't a link
    missing = tmp_path / "missing.txt"
    assert (Type == Type.UNKNOWN).match(missing)
