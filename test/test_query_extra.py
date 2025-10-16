"""Extra tests for Query and custom filters, including AlwaysTrue/AlwaysFalse and file creation helpers."""

import pytest
import pathlib
from pathql.query import Query
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.filters.base import Filter

class AlwaysTrue(Filter):
    def match(self, path, now=None, stat_result=None):
        return True

class AlwaysFalse(Filter):
    def match(self, path, now=None, stat_result=None):
        return False

def make_file(tmp_path, name="afile.txt"):
    file = tmp_path / name
    file.write_text("x")
    return file

def test_query_files_nonrecursive(tmp_path):
    f1 = make_file(tmp_path, "foo.txt")
    f2 = make_file(tmp_path, "bar.txt")
    q = Query(AlwaysTrue())
    files = list(q.files(tmp_path, recursive=False, files=True))
    names = sorted(f.name for f in files)
    assert set(names) >= {"foo.txt", "bar.txt"}

def test_query_files_dirs(tmp_path):
    d = tmp_path / "adir"
    d.mkdir()
    f = make_file(d, "foo.txt")
    q = Query(AlwaysTrue())
    # files=False yields directories
    dirs = list(q.files(tmp_path, recursive=True, files=False))
    assert any(x.is_dir() for x in dirs)

def test_query_files_stat_error(tmp_path):
    import sys
    PathBase = pathlib.WindowsPath if sys.platform.startswith('win') else pathlib.PosixPath
    class BadPath(PathBase):
        def stat(self):
            raise OSError("fail")
        def is_file(self):
            return True
    bad = BadPath(tmp_path / "bad.txt")
    q = Query(AlwaysTrue())
    # Directly test match error branch
    assert q.match(bad) is True

def test_query_match_stat_error(tmp_path):
    import sys
    PathBase = pathlib.WindowsPath if sys.platform.startswith('win') else pathlib.PosixPath
    class BadPath(PathBase):
        def stat(self):
            raise OSError("fail")
    bad = BadPath(tmp_path / "bad.txt")
    q = Query(AlwaysFalse())
    # Should not raise, just return False
    assert q.match(bad) is False
