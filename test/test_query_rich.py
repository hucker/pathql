"""Tests for Query on a rich filesystem, including size, suffix, stem, age, and type filters."""

import pathlib
import re
import pytest
from pathql.query import Query
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.filters.stem import Stem
from pathql.filters.age import AgeMinutes, AgeDays
from pathql.filters.type import Type


def test_all_files_bigger_than_50(rich_filesystem):
    root, now = rich_filesystem
    q = Query(Size() > 50)
    files = list(q.files(root, recursive=True, files=True, now=now))
    # All files with size > 50
    assert all(f.stat().st_size > 50 for f in files)
    # Should match g50.txt, g51.txt, h60.png, h61.png, e40.bmp, e41.bmp, b20.png (if >50), etc.
    for f in files:
        print(f"Matched: {f} size={f.stat().st_size}")


def test_txt_files_older_than_20_seconds(rich_filesystem):
    root, now = rich_filesystem
    q = Query((Suffix == "txt") & (AgeMinutes() > (20/60)))
    files = list(q.files(root, recursive=True, files=True, now=now))
    for f in files:
        assert f.suffix == ".txt"
        age_sec = now - f.stat().st_mtime
        assert age_sec > 20


def test_bmp_files_size_and_age(rich_filesystem):
    root, now = rich_filesystem
    q = Query((Suffix == "bmp") & (Size() > 30) & (AgeMinutes() > 0.01))
    files = list(q.files(root, recursive=True, files=True, now=now))
    for f in files:
        assert f.suffix == ".bmp"
        assert f.stat().st_size > 30
        assert (now - f.stat().st_mtime) > 0.01 * 60


def test_stem_pattern_and_type(rich_filesystem):
    root, now = rich_filesystem
    # Match files with stem starting with 'g' and are regular files
    q = Query((Stem(r"^g.*") & (Type == Type.FILE)))
    files = list(q.files(root, recursive=True, files=True, now=now))
    for f in files:
        assert f.stem.startswith("g")
        assert f.is_file()


def test_complex_combination(rich_filesystem):
    root, now = rich_filesystem
    # .txt files, size > 20, older than 10 seconds, stem contains 'd'
    q = Query((Suffix == "txt") & (Size() > 20) & (AgeMinutes() > (10/60)) & Stem(r"d"))
    files = list(q.files(root, recursive=True, files=True, now=now))
    for f in files:
        assert f.suffix == ".txt"
        assert f.stat().st_size > 20
        assert (now - f.stat().st_mtime) > 10
        assert "d" in f.stem


def test_all_files_type_file(rich_filesystem):
    root, now = rich_filesystem
    q = Query(Type == Type.FILE)
    files = list(q.files(root, recursive=True, files=True, now=now))
    for f in files:
        assert f.is_file()


def test_all_files_type_directory(rich_filesystem):
    root, now = rich_filesystem
    q = Query(Type == Type.DIRECTORY)
    files = list(q.files(root, recursive=True, files=False, now=now))
    for f in files:
        assert f.is_dir()
