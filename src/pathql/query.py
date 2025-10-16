import pathlib
from .filters.base import Filter
from typing import Iterator

import time

class Query(Filter):
    def __init__(self, filter_expr: Filter):
        self.filter_expr = filter_expr

    def files(self, path: 'pathlib.Path', recursive=True, files=True, now=None) -> Iterator['pathlib.Path']:
        if now is None:
            now = time.time()
        for p in path.rglob("*" if recursive else "*"):
            if files and not p.is_file():
                continue
            if self.filter_expr.match(p, now=now):
                yield p

    def match(self, path: 'pathlib.Path', now=None) -> bool:
        if now is None:
            import time
            now = time.time()
        return self.filter_expr.match(path, now=now)
