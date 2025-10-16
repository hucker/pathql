"""Tests for Query class and filter composition on a mini filesystem."""

import pathlib
import pytest
from pathql.query import Query
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.filters.stem import Stem
from pathql.filters.age import AgeMinutes, AgeDays
from pathql.filters.type import Type

@pytest.fixture
def mini_fs(tmp_path):
    # Create a small file structure for query tests
    f1 = tmp_path / "foo.txt"
    f2 = tmp_path / "bar.md"
    f3 = tmp_path / "baz.txt"
    d1 = tmp_path / "subdir"
    d1.mkdir()
    f4 = d1 / "qux.txt"
    f1.write_text("a" * 100)
    f2.write_text("b" * 200)
    f3.write_text("c" * 50)
    f4.write_text("d" * 300)
    return tmp_path

def test_query_size_and_suffix(mini_fs):
    q = Query((Size >= 100) & (Suffix == "txt"))
    files = list(q.files(mini_fs, recursive=True, files=True))
    names = sorted(f.name for f in files)
    assert names == ["foo.txt", "qux.txt"]

def test_query_or_and(mini_fs):
    q = Query(((Size > 250) & (Suffix == "txt")) | (Suffix == "md"))
    files = list(q.files(mini_fs, recursive=True, files=True))
    names = sorted(f.name for f in files)
    assert names == ["bar.md", "qux.txt"]



def test_query_in_operator(mini_fs):
    q = Query((Suffix == "txt") & (Size > 50))
    files = list(q.files(mini_fs, recursive=True, files=True))
    # Test 'in' operator for Suffix
    for f in files:
        assert "txt" in Suffix(["txt"])
        assert f.suffix == ".txt"

def test_query_type_file_and_dir(mini_fs):
    q_files = Query(Type == Type.FILE)
    q_dirs = Query(Type == Type.DIRECTORY)
    files = list(q_files.files(mini_fs, recursive=True, files=True))
    dirs = list(q_dirs.files(mini_fs, recursive=True, files=False))
    assert all(f.is_file() for f in files)
    assert all(d.is_dir() for d in dirs)

def test_query_complex(mini_fs):
    # .txt files with size > 50 or .md files with size < 300
    q = Query(((Suffix == "txt") & (Size > 50)) | ((Suffix == "md") & (Size < 300)))
    files = list(q.files(mini_fs, recursive=True, files=True))
    names = sorted(f.name for f in files)
    assert names == ["bar.md", "foo.txt", "qux.txt"]

