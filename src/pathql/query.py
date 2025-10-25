"""
Query engine for pathql: threaded producer-consumer file search and filtering.

This module defines the Query class, which uses a producer thread to walk the filesystem
and a consumer (main thread) to filter files using pathql filters.
"""

import datetime as dt
import pathlib
import queue
import threading
from typing import Iterator

from .filters.alias import DatetimeOrNone, StrOrPath, StrPathOrListOfStrPath
from .filters.base import Filter
from .filters.stat_proxy import StatProxy
from .result_set import ResultSet


class MatchAll(Filter):
    """A filter that matches all files."""

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxy,
        now: DatetimeOrNone = None,
    ):
        return True


class Query(Filter):
    """
    Query engine for pathql.

    Uses a threaded producer-consumer model to walk the filesystem and filter files.

    Args:
        filter_expr (Filter): The filter expression to apply to files.
    """

    def __init__(self, filter_expr: Filter | None = None):
        """
        Initialize Query.

        If you don't provide a filter_expression a MatchAll filter is used
        and all files in the folder will be match.

        Args:
            filter_expr (Filter): The filter expression to apply to files.
        """
        self.filter_expr = filter_expr or MatchAll()

        self.results = []

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxy,
        now: DatetimeOrNone = None,
    ) -> bool:
        """
        Check if a single path matches the filter expression.
        """
        if now is None:
            now = dt.datetime.now()
        return self.filter_expr.match(path, stat_proxy, now=now)

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
            if self.filter_expr.match(p, stat_proxy, now=now):
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
            if self.filter_expr.match(p, stat_proxy, now=now):
                yield p
        t.join()

    def files(
        self,
        paths: StrPathOrListOfStrPath,
        recursive: bool = True,
        files: bool = True,
        now: DatetimeOrNone = None,
        threaded: bool = False,
    ) -> Iterator[pathlib.Path]:
        """
        Yield files matching the filter expression for a single path or a list of paths.
        Handles both threaded and non-threaded modes.
        """
        if isinstance(paths, (str, pathlib.Path)):
            path_list = [paths]
        else:
            path_list = list(paths)
        path_list = [pathlib.Path(p) for p in path_list]
        for path in path_list:
            if threaded:
                yield from self._threaded_files(
                    path, recursive=recursive, files=files, now=now
                )
            else:
                yield from self._unthreaded_files(
                    path, recursive=recursive, files=files, now=now
                )

    def select(
        self,
        paths: StrPathOrListOfStrPath,
        recursive: bool = True,
        files: bool = True,
        now: DatetimeOrNone = None,
        threaded: bool = False,
    ) -> ResultSet:
        """
        Return a ResultSet of files matching the filter expression for a single path or a list of paths.
        """
        return ResultSet(self.files(paths, recursive, files, now, threaded))
