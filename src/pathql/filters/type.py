
import pathlib
from .base import Filter

class _TypeMeta(type):
    def __eq__(cls, other):
        return Type(other)
    def __or__(cls, other):
        if isinstance(other, Type):
            return Type({other})
        elif isinstance(other, str):
            return Type({other})
        elif isinstance(other, set):
            return Type(other)
        else:
            return NotImplemented
    def __ror__(cls, other):
        if isinstance(other, Type):
            return Type({other})
        elif isinstance(other, str):
            return Type({other})
        elif isinstance(other, set):
            return Type(other)
        else:
            return NotImplemented

class Type(Filter, metaclass=_TypeMeta):
    """
    Filter for file type: file, directory, link, or unknown.
    Usage: Type == Type.FILE, Type in {Type.FILE, Type.DIRECTORY}
    """
    FILE: str = "file"
    DIRECTORY: str = "directory"
    LINK: str = "link"
    UNKNOWN: str = "unknown"

    def __init__(self, type_name: str | set[str] | None = None) -> None:
        """
        Initialize a Type filter.
        Args:
            type_name: A type string or set of type strings (FILE, DIRECTORY, LINK, UNKNOWN)
        """
        if isinstance(type_name, set):
            self.type_names: set[str] = set(type_name)
        elif type_name is not None:
            self.type_names: set[str] = {type_name}
        else:
            self.type_names: set[str] = set()

    def match(self, path: 'pathlib.Path', now: float | None = None) -> bool:
        """
        Check if the path matches any of the specified types.
        Args:
            path: The pathlib.Path to check.
            now: Ignored (for interface compatibility).
        Returns:
            True if the path matches one of the types, else False.
        """
        import stat
        try:
            if not path.exists():
                return Type.UNKNOWN in self.type_names
            st = path.lstat()
            mode = st.st_mode
            type_map = {
                Type.FILE: stat.S_ISREG(mode),
                Type.DIRECTORY: stat.S_ISDIR(mode),
                Type.LINK: stat.S_ISLNK(mode),
            }
            for t in self.type_names:
                if type_map.get(t, False):
                    return True
            if Type.UNKNOWN in self.type_names:
                return not any(type_map.values())
            return False
        except Exception:
            # If lstat fails for any reason, treat as unknown if requested
            return Type.UNKNOWN in self.type_names


    def __eq__(self, other: object) -> 'Type':
        """Return a Type filter for equality comparison."""
        return Type(other)


    def __or__(self, other: object) -> 'Type':
        """Return a Type filter for set union."""
        if isinstance(other, Type):
            return Type(self.type_names | other.type_names)
        elif isinstance(other, str):
            return Type(self.type_names | {other})
        elif isinstance(other, set):
            return Type(self.type_names | set(other))
        else:
            return NotImplemented


    def __ror__(self, other: object) -> 'Type':
        """Return a Type filter for set union (reversed)."""
        if isinstance(other, Type):
            return Type(self.type_names | other.type_names)
        elif isinstance(other, str):
            return Type(self.type_names | {other})
        elif isinstance(other, set):
            return Type(self.type_names | set(other))
        else:
            return NotImplemented

    def __contains__(self, item: str) -> bool:
        """Check if a type string is in the filter's type set."""
        return item in self.type_names

    def __in__(self, items: set[str]) -> 'Type':
        """Return a Type filter for set membership."""
        return Type(items)
