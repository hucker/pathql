"""Extra tests for Query/custom filters, include AlwaysTrue/AlwaysFalse and file helpers."""

import datetime as dt
import pathlib
from typing import Any, cast

from pathql.filters.base import Filter
from pathql.filters.stat_proxy import StatProxy
from pathql.query import Query


class AlwaysTrue(Filter):
    """A filter that always matches."""

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxy,
        now: dt.datetime | None = None,
    ) -> bool:
        """Always returns True for any path."""
        return True


class AlwaysFalse(Filter):
    """A filter that never matches."""

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxy,
        now: dt.datetime | None = None,
    ) -> bool:
        """Always returns False for any path."""
        return False


def make_file(tmp_path: pathlib.Path, name: str = "a_file.txt") -> pathlib.Path:
    """Create a file with the given name in tmp_path."""
    file = tmp_path / name
    file.write_text("x")
    return file


def test_query_files_non_recursive(tmp_path: pathlib.Path):
    """Non-recursive file matching with AlwaysTrue filter."""
    # Arrange
    make_file(tmp_path, "foo.txt")
    make_file(tmp_path, "bar.txt")
    q = Query(AlwaysTrue())
    # Act
    files = list(q.files(tmp_path, recursive=False, files=True, threaded=False))
    names = sorted(f.name for f in files)
    # Assert
    assert set(names) >= {"foo.txt", "bar.txt"}


def test_query_files_dirs(tmp_path: pathlib.Path):
    """Directory matching with files=False option."""
    # Arrange
    d: pathlib.Path = tmp_path / "a_dir"
    d.mkdir()
    make_file(d, "foo.txt")
    q = Query(AlwaysTrue())
    # Act
    # files=False yields directories
    dirs = list(q.files(tmp_path, recursive=True, files=False, threaded=False))
    # Assert
    assert any(x.is_dir() for x in dirs)


def test_query_files_stat_error(tmp_path: pathlib.Path):
    """Query.match handles stat errors gracefully (returns True)."""

    # Arrange
    class BadPath:
        """Simulate a bad path"""

        def __init__(self, p: pathlib.Path) -> None:
            self._p = p

        def stat(self):
            """Simulate a stat error."""
            raise OSError("fail")

        def is_file(self):
            """Always return True for is_file()."""
            return True

        @property
        def name(self):
            """Return the name of the path."""
            return self._p.name

        def __fspath__(self) -> str:
            """Return the filesystem path as string."""
            return str(self._p)

    bad = BadPath(tmp_path / "bad.txt")
    q = Query(AlwaysTrue())
    # Act and Assert - should handle stat error and return True
    # Accessing _p for test purposes
    assert q.match(cast(Any, bad), StatProxy(bad._p)) is True  # type: ignore[attr-defined]


def test_query_match_stat_error(tmp_path: pathlib.Path):
    """Query.match handles stat errors gracefully (returns False)."""

    # Arrange
    class BadPath:
        """Simulate a bad path"""

        def __init__(self, p: pathlib.Path) -> None:
            """Simulate a bad path init."""
            self._p = p

        def stat(self):
            """Simulate a stat error."""
            raise OSError("fail")

        def __fspath__(self) -> str:
            """Return the filesystem path as string."""
            return str(self._p)

    bad = BadPath(tmp_path / "bad.txt")
    q = Query(AlwaysFalse())
    # Act and Assert - should not raise, just return False
    # Accessing _p for test purposes
    assert q.match(cast(Any, bad), StatProxy(bad._p)) is False  # type: ignore[attr-defined]
