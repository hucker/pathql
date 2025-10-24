"""Classes for filtering files by type: file, directory, link, or unknown (FileType)."""

import pathlib
import stat
from .alias import DatetimeOrNone, StatResultOrNone
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

    # This class does not require stat data to function
    _requires_stat: bool = False

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
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """Check if the path matches the specified type."""
        try:
            if self.type_name == FileType.LINK:
                return path.is_symlink()
            if not path.exists():
                return self.type_name == FileType.UNKNOWN
            st = stat_result if stat_result is not None else path.lstat()
            mode = st.st_mode
            if self.type_name == FileType.FILE:
                return stat.S_ISREG(mode)
            if self.type_name == FileType.DIRECTORY:
                return stat.S_ISDIR(mode)
            if self.type_name == FileType.UNKNOWN:
                return not (
                    stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_ISLNK(mode)
                )
            return False
        except Exception:
            return self.type_name == FileType.UNKNOWN
