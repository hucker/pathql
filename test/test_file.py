"""Tests for File filter, especially curly-brace extension patterns and case insensitivity."""

import pytest
import pathlib
from pathql.filters import File

@pytest.mark.parametrize(
    "filename, pattern, should_match",
    [
        ("foo.jpg", "foo.{jpg,png,bmp}", True),
        ("foo.png", "foo.{jpg,png,bmp}", True),
        ("foo.bmp", "foo.{jpg,png,bmp}", True),
        ("foo.gif", "foo.{jpg,png,bmp}", False),
        ("bar.jpg", "foo.{jpg,png,bmp}", False),
        ("foo.JPG", "foo.{jpg,png,bmp}", True),  # case-insensitive
        ("foo.PnG", "foo.{jpg,png,bmp}", True),  # case-insensitive
        ("foo", "foo.{jpg,png,bmp}", False),     # no extension
        ("foo.jpg.txt", "foo.{jpg,png,bmp}", False), # wrong extension
    ]
)
def test_file_curly_brace_suffix(tmp_path, filename, pattern, should_match):
    f = make_file(tmp_path, filename)
    assert File(pattern).match(f) is should_match


def make_file(tmp_path, name):
    file = tmp_path / name
    file.write_text("x")
    return file


@pytest.mark.parametrize(
    "filename, pattern, should_match",
    [
        # Exact match, case-insensitive
        ("Thumbs.db", "Thumbs.db", True),
        ("Thumbs.db", "thumbs.db", True),
        ("Thumbs.db", "other.db", False),
        # Wildcard extension
        ("foo.db", "*.db", True),
        ("foo.db", "*.txt", False),
        ("foo.txt", "*.db", False),
        ("foo.db", "foo.*", True),
        ("foo.db", "bar.*", False),
        ("foo.bmp", "*.bmp", True),
        ("bar.bmp", "*.bmp", True),
        ("foo.bmp", "foo.*", True),
        ("foo.bmp", "bar.*", False),
        # Wildcard stem
        ("foo123.db", "foo*", True),
        ("bar123.db", "foo*", False),
        ("foo123.db", "*123.db", True),
        ("foo123.db", "*23.db", True),
        ("foo123.db", "*99.db", False),
        # Path object as pattern
        ("foo.db", pathlib.Path("foo.db"), True),
        ("foo.db", pathlib.Path("other.db"), False),
    ]
)
def test_file_patterns(tmp_path, filename, pattern, should_match):
    f = make_file(tmp_path, filename)
    assert File(pattern).match(f) is should_match

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
