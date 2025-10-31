"""
Unit tests for normalize_path utility in pathql.utils.

Covers normalization of str, pathlib.Path, lists, tuples, nested structures, generators,
and error handling for unsupported types. Uses the AAA pattern.
"""

import pathlib
import pytest
from pathql.utils import normalize_path

def test_normalize_path_str():
    """Normalize single string path."""
    # Arrange
    p = "/tmp/foo.txt"
    # Act
    result = list(normalize_path(p))
    # Assert
    assert result == [pathlib.Path(p)]

def test_normalize_path_pathlib():
    """Normalize single pathlib.Path."""
    # Arrange
    p = pathlib.Path("/tmp/bar.txt")
    # Act
    result = list(normalize_path(p))
    # Assert
    assert result == [p]

def test_normalize_path_list():
    """Normalize list of paths."""
    # Arrange
    paths = ["/tmp/a.txt", pathlib.Path("/tmp/b.txt")]
    # Act
    result = list(normalize_path(paths))
    # Assert
    assert result == [pathlib.Path("/tmp/a.txt"), pathlib.Path("/tmp/b.txt")]

def test_normalize_path_tuple():
    """Normalize tuple of paths."""
    # Arrange
    paths = ("/tmp/a.txt", pathlib.Path("/tmp/b.txt"))
    # Act
    result = list(normalize_path(paths))
    # Assert
    assert result == [pathlib.Path("/tmp/a.txt"), pathlib.Path("/tmp/b.txt")]

def test_normalize_path_nested():
    """Normalize nested list/tuple of paths."""
    # Arrange
    paths = ["/tmp/a.txt", ("/tmp/b.txt", ["/tmp/c.txt", pathlib.Path("/tmp/d.txt")])]
    # Act
    result = list(normalize_path(paths))
    # Assert
    assert result == [
        pathlib.Path("/tmp/a.txt"),
        pathlib.Path("/tmp/b.txt"),
        pathlib.Path("/tmp/c.txt"),
        pathlib.Path("/tmp/d.txt"),
    ]

def test_normalize_path_generator():
    """Normalize generator of paths."""
    # Arrange
    def gen():
        yield "/tmp/a.txt"
        yield pathlib.Path("/tmp/b.txt")
    # Act
    result = list(normalize_path(gen()))
    # Assert
    assert result == [pathlib.Path("/tmp/a.txt"), pathlib.Path("/tmp/b.txt")]

def test_normalize_path_invalid_type():
    """Raise ValueError for unsupported type."""
    # Arrange
    class Dummy: pass
    dummy = Dummy()
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid paths argument"):
        list(normalize_path(dummy))