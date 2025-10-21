"""Actions for creating zip archives from query matches."""

from __future__ import annotations

import zipfile
import pathlib
from typing import List, Any

from .utils import iter_matches

def zip_matches(
    root: pathlib.Path,
    query: Any,
    target_zip: pathlib.Path,
    *,
    preserve_dir_structure: bool = True,
    compress: bool = True,
    dry_run: bool = False,
    ) -> List[pathlib.Path]:
    """Create a zip archive from query matches and return added paths.

    `query` is intentionally typed as Any to avoid importing the Query
    type into this module and to keep the dependency surface small.
    """

    root = pathlib.Path(root)
    matches = [p for p in iter_matches(root, query) if p.exists()]

    if dry_run:
        return matches

    target_zip.parent.mkdir(parents=True, exist_ok=True)
    compress_mode = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
    added: List[pathlib.Path] = []

    with zipfile.ZipFile(target_zip, "w", compression=compress_mode) as zf:
        for p in matches:
            if p.is_dir():
                continue
            try:
                archive_name = p.relative_to(root) if preserve_dir_structure else p.name
            except ValueError:
                archive_name = p.name
            zf.write(p, arcname=str(archive_name))
            added.append(p)

    return added
