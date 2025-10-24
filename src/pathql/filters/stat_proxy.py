"""
StatProxy: Lazy, cached stat() for PathQL filters, with stat call counting.
"""

import os
import pathlib


class StatProxy:
    """
    Lazily calls .stat() on a pathlib.Path, caching the result and counting calls.
    """

    def __init__(self, path: pathlib.Path):
        self.path = path
        self._stat = None
        self._stat_error = None
        self._stat_calls = 0

    def stat(self) -> os.stat_result:
        self._stat_calls += 1
        if self._stat is None and self._stat_error is None:
            try:
                self._stat = self.path.stat()
            except Exception as e:
                self._stat_error = e
                raise
        if self._stat_error:
            raise self._stat_error
        return self._stat

    @property
    def stat_calls(self) -> int:
        """Return the number of times stat() was called on this proxy."""
        return self._stat_calls
        return self._stat_calls
