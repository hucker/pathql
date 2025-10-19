"""
Tests for Type filter, covering file, directory, and symlink detection.
"""
import pathlib
import pytest
import sys
from pathql.filters.type import Type

def test_type_file(tmp_path: pathlib.Path) -> None:
    """
    Test that Type.FILE matches a regular file.

    - Arrange: Create a regular file.
    - Act: Apply Type.FILE filter.
    - Assert: Verify the file matches.
    """
    # Arrange
    f = tmp_path / "a.txt"
    f.write_text("A")

    # Act and Assert
    assert (Type == Type.FILE).match(f)

def test_type_directory(tmp_path: pathlib.Path) -> None:
    """
    Test that Type.DIRECTORY matches a directory.

    - Arrange: Create a directory.
    - Act: Apply Type.DIRECTORY filter.
    - Assert: Verify the directory matches.
    """
    # Arrange
    d = tmp_path / "dir"
    d.mkdir()

    # Act and Assert
    assert (Type == Type.DIRECTORY).match(d)

def test_type_link(tmp_path: pathlib.Path) -> None:
    """
    Test that Type.LINK matches a symlink and not file or directory.

    - Arrange: Create a symlink.
    - Act: Apply Type.LINK filter.
    - Assert: Verify the symlink matches.
    """
    # Arrange
    if sys.platform.startswith("win"):
        pytest.skip("Symlink tests are skipped on Windows.")
    f = tmp_path / "foo.txt"
    f.write_text("hello")
    link = tmp_path / "foo_link.txt"
    link.symlink_to(f)

    # Act and Assert
    assert (Type == Type.LINK).match(link)
    assert not (Type == Type.FILE).match(link)

def test_type_union_and_set(tmp_path: pathlib.Path) -> None:
    """
    Test Type filter with set union and direct string/set construction.

    - Arrange: Create a file and a directory.
    - Act: Apply union and set filters.
    - Assert: Verify matching results.
    """
    # Arrange
    f = tmp_path / "a.txt"
    f.write_text("A")
    d = tmp_path / "adir"
    d.mkdir()

    # Act and Assert
    type_union = {Type.FILE, Type.DIRECTORY}
    assert (Type == type_union).match(f)
    assert (Type == type_union).match(d)
    assert Type("file").match(f)
    assert Type("directory").match(d)
    assert Type({"file", "directory"}).match(f)
    assert Type({"file", "directory"}).match(d)

def test_type_contains() -> None:
    """
    Test __contains__ for Type filter set membership.

    - Arrange: Create a Type filter with multiple types.
    - Act: Check membership.
    - Assert: Verify membership results.
    """
    # Arrange
    t = Type({Type.FILE, Type.DIRECTORY})

    # Act and Assert
    assert Type.FILE in t
    assert Type.DIRECTORY in t
    assert Type.LINK not in t

def test_type_or_and_ror() -> None:
    """
    Test __or__ and __ror__ operator overloads for Type filter.

    - Arrange: Create Type filters.
    - Act: Apply union operations.
    - Assert: Verify union results.
    """
    # Arrange
    t1 = Type(Type.FILE)
    t2 = Type(Type.DIRECTORY)

    # Act
    t3 = t1 | t2
    t4 = t2.__ror__(t1)

    # Assert
    assert Type.FILE in t3.type_names and Type.DIRECTORY in t3.type_names
    assert t3.type_names == t4.type_names

def test_type_error_handling(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """
    Test error handling and UNKNOWN logic in Type filter.

    - Arrange: Create a bad path and a broken symlink.
    - Act: Apply Type filters.
    - Assert: Verify error handling and UNKNOWN logic.
    """
    # Arrange
    f = tmp_path / "err.txt"
    f.write_text("E")
    class BadPath(type(f)):
        def exists(self) -> bool:
            return True
        def lstat(self):
            raise OSError("fail")
    bad = BadPath(f)

    # Act and Assert
    assert Type(Type.UNKNOWN).match(bad)
    assert not Type(Type.FILE).match(bad)
    if sys.platform.startswith("win"):
        pytest.skip("Symlink tests are skipped on Windows.")
    broken = tmp_path / "broken_link"
    broken.symlink_to(tmp_path / "does_not_exist.txt")
    assert (Type == Type.LINK).match(broken)
