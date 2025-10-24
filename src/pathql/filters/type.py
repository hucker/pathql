"""Classes for filtering files by type: file, directory, link, or unknown."""

import pathlib
import stat
from .alias import DatetimeOrNone, StatResultOrNone
from .base import Filter

class Type(Filter):
    """
    Filter for file type: file, directory, link, or unknown.

    Usage:
        Type().file
        Type().directory
        Type().link
        Type().unknown
    """

    FILE: str = "file"
    DIRECTORY: str = "directory"
    LINK: str = "link"
    UNKNOWN: str = "unknown"

    def __init__(self, type_name: str | None = None) -> None:
        self.type_name = type_name

    @property
    def file(self) -> "Type":
        """Return a Type filter for regular files."""
        return Type(Type.FILE)

    @property
    def directory(self) -> "Type":
        """Return a Type filter for directories."""
        return Type(Type.DIRECTORY)

    @property
    def link(self) -> "Type":
        """Return a Type filter for symlinks."""
        return Type(Type.LINK)

    @property
    def unknown(self) -> "Type":
        """Return a Type filter for unknown types."""
        return Type(Type.UNKNOWN)

    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """Check if the path matches the specified type."""
        try:
            if self.type_name == Type.LINK:
                return path.is_symlink()
            if not path.exists():
                return self.type_name == Type.UNKNOWN
            st = stat_result if stat_result is not None else path.lstat()
            mode = st.st_mode
            if self.type_name == Type.FILE:
                return stat.S_ISREG(mode)
            if self.type_name == Type.DIRECTORY:
                return stat.S_ISDIR(mode)
            if self.type_name == Type.UNKNOWN:
                return not (stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_ISLNK(mode))
            return False
        except Exception:
            return self.type_name == Type.UNKNOWN