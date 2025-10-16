"""Extra tests for Suffix and Ext filters, including nosplit and case-insensitive matching."""

import pytest
import pathlib
from pathql.filters.suffix import Suffix, Ext

def make_file(tmp_path, name):
    file = tmp_path / name
    file.write_text("x")
    return file

def test_suffix_basic(tmp_path):
    file = make_file(tmp_path, "foo.txt")
    assert Suffix("txt").match(file)
    assert not Suffix("md").match(file)
    assert Suffix(["txt", "md"]).match(file)
    assert Suffix("txt md").match(file)
    assert Suffix(["TXT"]).match(file)  # case-insensitive
    assert Ext("txt").match(file)  # alias works

def test_suffix_nosplit(tmp_path):
    file = make_file(tmp_path, "foo.bar baz")
    # nosplit: treat as one extension
    assert Suffix("bar baz", nosplit=True).match(file)
    assert not Suffix("bar baz").match(file)

def test_suffix_empty_patterns(tmp_path):
    file = make_file(tmp_path, "foo.txt")
    with pytest.raises(ValueError):
        Suffix().match(file)

def test_suffix_operator_overloads(tmp_path):
    file = make_file(tmp_path, "foo.txt")
    # __eq__
    assert Suffix(["txt"]) == Suffix(["txt"])
    # __contains__
    assert "txt" in Suffix("txt md")
    # __call__
    assert Suffix("txt")(["txt"]).match(file)
    # __class_getitem__
    assert Suffix["txt"].match(file)
    assert Suffix["txt", "md"].match(file)
    # Only test operator overloads that are meaningful and supported by the API
