"""High-level file actions (zip, delete, move, archive helpers).

This package exposes compact, testable helpers that operate over the
project's Query/Filter API. Functions are intentionally small and accept
`dry_run` and `confirm` hooks to make testing safe.
"""

from .utils import iter_matches
from .zip import zip_matches
from .delete import delete_matches

__all__ = [
    "iter_matches",
    "zip_matches",
    "delete_matches",
]
