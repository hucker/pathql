import pytest
import pathlib
from pathql.filters import File

def make_file(tmp_path, name):
    file = tmp_path / name
    file.write_text("x")
    return file

def test_file_exact(tmp_path):
    f = make_file(tmp_path, "Thumbs.db")
    assert File("Thumbs.db").match(f)
    assert File("thumbs.db").match(f)
    assert not File("other.db").match(f)

def test_file_wildcard(tmp_path):
    f = make_file(tmp_path, "foo.db")
    assert File("*.db").match(f)
    assert not File("*.txt").match(f)

def test_file_macro(tmp_path):
    f = make_file(tmp_path, "foo.db")
    assert File("{stem}.db").match(f)
    assert not File("{stem}.txt").match(f)

def test_file_regex(tmp_path):
    f = make_file(tmp_path, "foo_123.txt")
    assert File(r"^foo_\d+\.txt$").match(f)
    assert not File(r"^bar_\d+\.txt$").match(f)

def test_file_as_stem_and_suffix(tmp_path):
    f = make_file(tmp_path, "foo.db")
    file_filter = File("foo.db")
    result = file_filter.as_stem_and_suffix()
    assert result is not None
    stem, suffix = result
    assert stem.match(f)
    assert suffix.match(f)
    # Not for wildcards
    assert File("*.db").as_stem_and_suffix() is None
    assert File(r"^foo.*$").as_stem_and_suffix() is None
