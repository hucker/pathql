from __future__ import annotations

import pathlib
import shutil
from typing import List, Optional, Callable

from .utils import iter_matches


def delete_matches(
    root: pathlib.Path,
    query,
    *,
    recursive: bool = False,
    dry_run: bool = False,
    confirm: Optional[Callable[[pathlib.Path], bool]] = None,
) -> List[pathlib.Path]:
    root = pathlib.Path(root)
    candidates = [p for p in iter_matches(root, query)]

    deleted: List[pathlib.Path] = []
    for p in candidates:
        if confirm is not None and not confirm(p):
            continue
        if dry_run:
            deleted.append(p)
            continue
        try:
            if p.is_symlink() or p.is_file():
                p.unlink()
                deleted.append(p)
            elif p.is_dir():
                if recursive:
                    shutil.rmtree(p)
                    deleted.append(p)
                else:
                    try:
                        p.rmdir()
                        deleted.append(p)
                    except OSError:
                        continue
        except OSError:
            continue

    return deleted
