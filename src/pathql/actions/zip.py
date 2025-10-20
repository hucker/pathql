from __future__ import annotations

import zipfile
import pathlib
from typing import List

from .utils import iter_matches


def zip_matches(
    root: pathlib.Path,
    query,
    target_zip: pathlib.Path,
    *,
    preserve_dir_structure: bool = True,
    compress: bool = True,
    dry_run: bool = False,
) -> List[pathlib.Path]:
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
                arcname = p.relative_to(root) if preserve_dir_structure else p.name
            except Exception:
                arcname = p.name
            zf.write(p, arcname=str(arcname))
            added.append(p)

    return added
