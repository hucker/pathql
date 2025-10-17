"""
Query engine for pathql: threaded producer-consumer file search and filtering.

This module defines the Query class, which uses a producer thread to walk the filesystem and a consumer (main thread) to filter files using pathql filters.
"""
import os
import pathlib
import threading
import queue
import time
from typing import Iterator

from .filters.base import Filter

class Query(Filter):
    """
    Query engine for pathql.

    Uses a threaded producer-consumer model to walk the filesystem and filter files.

    Args:
        filter_expr (Filter): The filter expression to apply to files.
    """

    def __init__(self, filter_expr: Filter):
        """
        Initialize Query.

        Args:
            filter_expr (Filter): The filter expression to apply to files.
        """
        self.filter_expr = filter_expr

    def match(
        self,
        path: pathlib.Path,
        now: float | None = None,
        stat_result: os.stat_result | None = None
    ) -> bool:
        """
        Check if a single path matches the filter expression.

        Args:
            path (pathlib.Path): File or directory to check.
            now (float, optional): Reference time for filters. Defaults to current time.
            stat_result (os.stat_result, optional): Cached stat result. If None, will stat the path.

        Returns:
            bool: True if the path matches the filter, False otherwise.
        """
        if now is None:
            now = time.time()
        if stat_result is None:
            try:
                stat_result = path.stat()
            except Exception:
                stat_result = None
        return self.filter_expr.match(path, now=now, stat_result=stat_result)

    def _unthreaded_files(
        self,
        path: pathlib.Path,
        recursive: bool = True,
        files: bool = True,
        now: float | None = None,
    ) -> Iterator[pathlib.Path]:
        """
        Yield files matching the filter expression using a single-threaded approach (no queue/thread).

        Args:
            path (pathlib.Path): Root directory to search.
            recursive (bool): If True, search recursively. If False, only top-level files.
            files (bool): If True, yield only files (not directories).
            now (float, optional): Reference time for filters. Defaults to current time.

        Yields:
            pathlib.Path: Files matching the filter expression.
        """
        if now is None:
            now = time.time()
        iterator = path.rglob("*") if recursive else path.glob("*")
        for p in iterator:
            if files and not p.is_file():
                continue
            try:
                stat_result = p.stat()
            except Exception:
                stat_result = None
            if self.filter_expr.match(p, now=now, stat_result=stat_result):
                yield p

    def _threaded_files(
        self,
        path: pathlib.Path,
        recursive: bool = True,
        files: bool = True,
        now: float | None = None,
    ) -> Iterator[pathlib.Path]:
        """
        Yield files matching the filter expression using a threaded producer-consumer model.

        Args:
            path (pathlib.Path): Root directory to search.
            recursive (bool): If True, search recursively. If False, only top-level files.
            files (bool): If True, yield only files (not directories).
            now (float, optional): Reference time for filters. Defaults to current time.

        Yields:
            pathlib.Path: Files matching the filter expression.
        """
        if now is None:
            now = time.time()
        q: queue.Queue[tuple[pathlib.Path, object | None]] = queue.Queue(maxsize=10)

        def producer():
            iterator = path.rglob("*") if recursive else path.glob("*")
            for p in iterator:
                if files and not p.is_file():
                    continue
                try:
                    stat_result = p.stat()
                except Exception:
                    stat_result = None
                q.put((p, stat_result))
            q.put(None)  # Sentinel to signal completion

        t = threading.Thread(target=producer, daemon=True)
        t.start()
        while True:
            item = q.get()
            if item is None:
                break
            p, stat_result = item
            if self.filter_expr.match(p, now=now, stat_result=stat_result):
                yield p
        t.join()

    def files(
        self,
        path: pathlib.Path,
        recursive: bool = True,
        files: bool = True,
        now: float | None = None,
        threaded: bool = False,
    ) -> Iterator[pathlib.Path]:
        """
        Yield files matching the filter expression using either threaded or non-threaded mode.

        Args:
            path (pathlib.Path): Root directory to search.
            recursive (bool): If True, search recursively. If False, only top-level files.
            files (bool): If True, yield only files (not directories).
            now (float, optional): Reference time for filters. Defaults to current time.
            threaded (bool): If True, use threaded producer-consumer model. If False, use single-threaded.

        Yields:
            pathlib.Path: Files matching the filter expression.
        """
        if threaded:
            yield from self._threaded_files(
                path, recursive=recursive, files=files, now=now
            )
        else:
            yield from self._unthreaded_files(
                path, recursive=recursive, files=files, now=now
            )
