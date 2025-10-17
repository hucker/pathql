"""Extra tests for Query and custom filters, including AlwaysTrue/AlwaysFalse and file creation helpers."""
import os
import pathlib
import sys
import pytest
import pathlib
from pathql.query import Query
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.filters.base import Filter

class AlwaysTrue(Filter):
    def match(self, path, now=None, stat_result: os.stat_result | None = None) -> bool:
        """Always returns True for any path."""
        return True

class AlwaysFalse(Filter):
    def match(self, path:pathlib.Path, now:float|None=None, stat_result: os.stat_result | None = None) -> bool:
        """Always returns False for any path."""
        return False

def make_file(tmp_path:pathlib.Path, name:str="afile.txt")->pathlib.Path:
    """Create a file with the given name in tmp_path."""
    file = tmp_path / name
    file.write_text("x")
    return file

def test_query_files_nonrecursive(tmp_path:pathlib.Path):
    """Test non-recursive file matching with AlwaysTrue filter."""
    f1: pathlib.Path = make_file(tmp_path, "foo.txt")
    f2: pathlib.Path = make_file(tmp_path, "bar.txt")
    q = Query(AlwaysTrue())
    files = list(q.files(tmp_path, recursive=False, files=True, threaded=False))
    names = sorted(f.name for f in files)
    assert set(names) >= {"foo.txt", "bar.txt"}

def test_query_files_dirs(tmp_path:pathlib.Path):
    """Test directory matching with files=False option."""
    d:pathlib.Path = tmp_path / "adir"
    d.mkdir()
    f:pathlib.Path = make_file(d, "foo.txt")
    q = Query(AlwaysTrue())
    # files=False yields directories
    dirs = list(q.files(tmp_path, recursive=True, files=False, threaded=False))
    assert any(x.is_dir() for x in dirs)

def test_query_files_stat_error(tmp_path:pathlib.Path):
    """Test Query.match handles stat errors gracefully (returns True)."""
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

def test_query_match_stat_error(tmp_path:pathlib.Path):
    """Test Query.match handles stat errors gracefully (returns False)."""
    import sys
    PathBase = pathlib.WindowsPath if sys.platform.startswith('win') else pathlib.PosixPath
    class BadPath(PathBase):
        def stat(self):
            raise OSError("fail")
    bad = BadPath(tmp_path / "bad.txt")
    q = Query(AlwaysFalse())
    # Should not raise, just return False
    assert q.match(bad) is False
