"""
Query engine for pathql: threaded producer-consumer file search and filtering.

This module defines the Query class, which uses a producer thread to walk the filesystem
and a consumer (main thread) to filter files using pathql filters.

Supports both classic constructor configuration and fluent/builder-style chained setup:
    Query(from_paths="...", where_expr=Suffix() == ".txt")
    Query().from_paths("...").where(Suffix() == ".txt")
"""

import datetime as dt
import pathlib
import queue
import threading
from typing import Iterator

from .filters.alias import (
    DatetimeOrNone,
    StatProxyOrNone,
    StrOrPath,
    StrPathOrListOfStrPath,
)
from .filters.base import AllowAll, Filter
from .filters.stat_proxy import StatProxy
from .result_set import ResultSet


class Query(Filter):
    """
    Query engine for pathql.

    Uses a threaded producer-consumer model to walk the filesystem and filter files.

    Supports both classic constructor configuration and fluent/builder-style chained setup.
    """

    def __init__(
        self,
        *,
        from_paths: StrPathOrListOfStrPath = ".",
        where_expr: Filter | None = None,
        recursive: bool = True,
        files_only: bool = True,
        now: DatetimeOrNone = None,
        threaded: bool = False,
    ) -> None:
        """
        Initialize Query.

        Args:
            from_paths (str | Path | list | tuple): Default path(s) for files/select.
            where_expr (Filter): The filter expression to apply to each file found in from_path
            recursive (bool): Whether to search recursively.
            files_only (bool): Whether to include only files.
            now (datetime | None): Reference time for filters.
            threaded (bool): Whether to use threaded search.
        """
        self._from_paths: StrPathOrListOfStrPath = from_paths
        self._where_expr: Filter = where_expr or AllowAll()
        self._recursive: bool = recursive
        self._files_only: bool = files_only
        self._now: DatetimeOrNone = now
        self._threaded: bool = threaded

    # --- Builder/Fluent API methods ---
    def from_paths(self, paths: StrPathOrListOfStrPath) -> "Query":
        """Set the source path(s) for the query."""
        self._from_paths = paths
        return self

    def where(self, expr: Filter) -> "Query":
        """Set the filter expression for the query."""
        self._where_expr = expr
        return self

    def recursive(self, value: bool = True) -> "Query":
        """Set whether to search recursively."""
        self._recursive = value
        return self

    def files_only(self, value: bool = True) -> "Query":
        """Set whether to include only files."""
        self._files_only = value
        return self

    def at_time(self, now: DatetimeOrNone) -> "Query":
        """Set the reference time for filters."""
        self._now = now
        return self

    def threaded(self, value: bool = True) -> "Query":
        """Set whether to use threaded search."""
        self._threaded = value
        return self

    # --- Property getters for testing fluent interface ---
    # These are provided to allow tests to verify internal state after using builder methods.
    @property
    def get_from_paths(self):
        """For test support: get internal from_paths value."""
        return self._from_paths

    @property
    def get_where_expr(self):
        """For test support: get internal where_expr value."""
        return self._where_expr

    @property
    def get_recursive(self):
        """For test support: get internal recursive value."""
        return self._recursive

    @property
    def get_files_only(self):
        """For test support: get internal files_only value."""
        return self._files_only

    @property
    def get_now(self):
        """For test support: get internal now value."""
        return self._now

    @property
    def get_threaded(self):
        """For test support: get internal threaded value."""
        return self._threaded

    # --- Query logic ---
    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ) -> bool:
        """
        Check if a single path matches the filter expression.
        """
        if now is None:
            now = dt.datetime.now()
        return self._where_expr.match(path, stat_proxy, now=now)

    def _unthreaded_files(
        self,
        path: StrOrPath,
        recursive: bool = True,
        files: bool = True,
        now: DatetimeOrNone = None,
    ) -> Iterator[pathlib.Path]:
        """
        Yield files matching filter expression using a single-threaded approach (no queue/thread).
        """
        if isinstance(path, str):
            path = pathlib.Path(path)
        if now is None:
            now = dt.datetime.now()
        iterator = path.rglob("*") if recursive else path.glob("*")
        for p in iterator:
            if files and not p.is_file():
                continue
            stat_proxy = StatProxy(p)
            if self._where_expr.match(p, stat_proxy, now=now):
                yield p

    def _threaded_files(
        self,
        path: StrOrPath,
        recursive: bool = True,
        files: bool = True,
        now: DatetimeOrNone = None,
    ) -> Iterator[pathlib.Path]:
        """
        Yield files matching the filter expression using a threaded producer-consumer model.
        """
        if isinstance(path, str):
            path = pathlib.Path(path)
        if now is None:
            now = dt.datetime.now()
        q: queue.Queue[pathlib.Path | None] = queue.Queue(maxsize=10)

        def producer():
            iterator = path.rglob("*") if recursive else path.glob("*")
            for p in iterator:
                if files and not p.is_file():
                    continue
                q.put(p)
            q.put(None)  # Sentinel to signal completion

        t = threading.Thread(target=producer, daemon=True)
        t.start()
        while True:
            p = q.get()
            if p is None:
                break
            stat_proxy = StatProxy(p)
            if self._where_expr.match(p, stat_proxy, now=now):
                yield p
        t.join()

    def files(
        self,
        from_paths: StrPathOrListOfStrPath | None = None,
        recursive: bool | None = None,
        files_only: bool | None = None,
        now: DatetimeOrNone = None,
        threaded: bool | None = None,
    ) -> Iterator[pathlib.Path]:
        """
        Yield files matching the filter expression for a single path or a list of paths.
        Handles both threaded and non-threaded modes. Uses default from_path if paths not given.
        """
        if from_paths is None:
            from_paths = self._from_paths
        if recursive is None:
            recursive = self._recursive
        if files_only is None:
            files_only = self._files_only
        if now is None:
            now = self._now or dt.datetime.now()
        if threaded is None:
            threaded = self._threaded
        if isinstance(from_paths, (str, pathlib.Path)):
            path_list = [from_paths]
        else:
            path_list = list(from_paths)
        path_list = [pathlib.Path(p) for p in path_list]
        for path in path_list:
            if threaded:
                yield from self._threaded_files(
                    path, recursive=recursive, files=files_only, now=now
                )
            else:
                yield from self._unthreaded_files(
                    path, recursive=recursive, files=files_only, now=now
                )

    def select(
        self,
        from_paths: StrPathOrListOfStrPath | None = None,
        recursive: bool | None = None,
        files_only: bool | None = None,
        now: DatetimeOrNone = None,
        threaded: bool | None = None,
    ) -> ResultSet:
        """
        Return a ResultSet of files matching the filter expr for a path or a list of paths.
        Uses default from_path if paths not given.
        """
        return ResultSet(self.files(from_paths, recursive, files_only, now, threaded))
