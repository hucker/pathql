from __future__ import annotations

import pathlib
from typing import Iterable

from pathql.filters.base import Filter
from pathql.query import Query


def iter_matches(root: pathlib.Path, query:Query) -> Iterable[pathlib.Path]:
    """Yield Path objects matching `query` under `root`.

    Supported query shapes:
      - callable(root) -> Iterable[Path]
      - object with .run(root) or .search(root)
      - a Filter instance (will walk root and call filter.match(path, stat_result=...))
    """
    root = pathlib.Path(root)

    if callable(query):
        yield from query(root)
        return

    if hasattr(query, "run"):
        yield from query.run(root)
        return

    if hasattr(query, "search"):
        yield from query.search(root)
        return

    if isinstance(query, Filter):
        for p in root.rglob("*"):
            try:
                st = p.stat()
            except OSError:
                continue
            try:
                if query.match(p, stat_result=st):
                    yield p
            except Exception:
                continue
        return

    raise TypeError("unsupported query type; pass callable, object with run/search, or a Filter")
