import pathlib
import pytest
import sys
from pathql.filters.type import Type

def test_type_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("A")
    assert (Type == Type.FILE).match(f)

def test_type_directory(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    assert (Type == Type.DIRECTORY).match(d)

def test_type_link(tmp_path):
    if sys.platform.startswith("win"):
        pytest.skip("Symlink tests are skipped on Windows.")
    f = tmp_path / "foo.txt"
    f.write_text("hello")
    link = tmp_path / "foo_link.txt"
    link.symlink_to(f)
    assert (Type == Type.LINK).match(link)
    assert not (Type == Type.FILE).match(link)
    assert not (Type == Type.DIRECTORY).match(link)

def test_type_unknown(tmp_path):
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
