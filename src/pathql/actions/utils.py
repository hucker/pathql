from __future__ import annotations

import pathlib

from ..filters.alias import StrPathOrListOfStrPath


def normalize_file_str_list(file_list: StrPathOrListOfStrPath) -> list[pathlib.Path]:
    """Normalize list of paths given as str/Path, or list of str/Path into a flat list of Path objects."""
    if isinstance(file_list, str):
        return [pathlib.Path(file_list)]
    if isinstance(file_list, pathlib.Path):
        return [file_list]

    normalized_list: list[pathlib.Path] = []
    for item in file_list:
        normalized_list.append(pathlib.Path(item))

    return normalized_list


# def iter_matches(root: pathlib.Path, query: Query) -> Iterable[pathlib.Path]:
#     """Yield Path objects matching `query` under `root`.

#     Supported query shapes:
#       - callable(root) -> Iterable[Path]
#       - object with .run(root) or .search(root)
#       - a Filter instance (will walk root and call filter.match(path, stat_result=...))
#     """
#     root = pathlib.Path(root)

#     if callable(query):
#         yield from query(root)
#         return

#     if hasattr(query, "run"):
#         yield from query.run(root)
#         return

#     if hasattr(query, "search"):
#         yield from query.search(root)
#         return

#     if isinstance(query, Filter):
#         for p in root.rglob("*"):
#             try:
#                 st = p.stat()
#             except OSError:
#                 continue
#             try:
#                 if query.match(p, stat_result=st):
#                     yield p
#             except Exception:
#                 continue
#         return

#     raise TypeError(
#         "unsupported query type; pass callable, object with run/search, or a Filter"
#     )
