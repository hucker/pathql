"""Classes for filtering files by type: file, directory, link, or unknown (FileType)."""

import pathlib
import stat

from .alias import DatetimeOrNone
from .base import Filter


class FileType(Filter):
    """
    Filter for file type: file, directory, link, or unknown.

    Usage:
        FileType().file
        FileType().directory
        FileType().link
        FileType().unknown
    """

    # StatProxy-based, no requires_stat logic needed

    FILE: str = "file"
    DIRECTORY: str = "directory"
    LINK: str = "link"
    UNKNOWN: str = "unknown"

    def __init__(self, type_name: str | None = None) -> None:
        self.type_name = type_name

    @property
    def file(self) -> "FileType":
        """Return a FileType filter for regular files."""
        return FileType(FileType.FILE)

    @property
    def directory(self) -> "FileType":
        """Return a FileType filter for directories."""
        return FileType(FileType.DIRECTORY)

    @property
    def link(self) -> "FileType":
        """Return a FileType filter for symlinks."""
        return FileType(FileType.LINK)

    @property
    def unknown(self) -> "FileType":
        """Return a FileType filter for unknown types."""
        return FileType(FileType.UNKNOWN)

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: "StatProxy",  # type: ignore[name-defined]
        now: DatetimeOrNone = None,
    ) -> bool:
        """Check if the path matches the specified type."""
        try:
            if self.type_name == FileType.LINK:
                return path.is_symlink()
            if not path.exists():
                return self.type_name == FileType.UNKNOWN
            st = stat_proxy.stat()
            mode = st.st_mode
            if self.type_name == FileType.FILE:
                # Only return True for regular files that are NOT symlinks
                return stat.S_ISREG(mode) and not path.is_symlink()
            if self.type_name == FileType.DIRECTORY:
                return stat.S_ISDIR(mode)
            if self.type_name == FileType.UNKNOWN:
                return not (
                    stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_ISLNK(mode)
                )
            return False
        except Exception:  # type: ignore[broad-except]
            return self.type_name == FileType.UNKNOWN
