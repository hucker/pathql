"""
Unit tests for file_actions: copy, move, and delete operations.

Creates a temporary multi-level 'source' directory and a 'destination' directory for each test.
Verifies correct file manipulation for flat and nested structures using AAA (Arrange, Act, Assert) comments.
"""
import pathlib

import pytest

from pathql.actions import file_actions
from pathql.filters.suffix import Suffix
from pathql.query import Query

TREE = {
    "source": [
        "a.txt",
        "b.txt",
        {"sub1": ["c.txt"]},
        {"sub2": ["d.txt"]},
    ]
}

def create_tree(base: pathlib.Path, tree: dict) -> None:
    """Recursively create folders and files from a nested dictionary structure.

    Args:
        base: The base directory to create the tree in.
        tree: Dictionary where keys are folder names and values are lists of filenames or subfolder dicts.
    """
    for folder, items in tree.items():
        folder_path = base / folder
        folder_path.mkdir()
        for item in items:
            if isinstance(item, str):
                (folder_path / item).write_text(item[0])  # Write first letter as content
            elif isinstance(item, dict):
                create_tree(folder_path, item)

@pytest.fixture
def test_dirs(tmp_path) -> tuple[pathlib.Path, pathlib.Path]:
    """Pytest fixture that creates a temporary 'source' and 'destination' directory with a nested file structure.

    Returns:
        Tuple of (source, destination) pathlib.Path objects.
    """
    create_tree(tmp_path, TREE)
    source: pathlib.Path = tmp_path / "source"
    destination: pathlib.Path = tmp_path / "destination"
    destination.mkdir()
    return source, destination

def test_copy_files_flat(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test copying flat files from source to destination."""

    # Arrange
    source: pathlib.Path
    destination: pathlib.Path
    source, destination = test_dirs
    q = Query(Suffix("txt"))
    files = list(q.files(source, recursive=False))

    # Act
    result = file_actions.copy_files(files, destination)

    # Assert
    assert result.status
    for name in ["a.txt", "b.txt"]:
        assert (destination / name).exists(), f"File {name} should exist in flat destination"

def test_copy_files_nested(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test copying nested files from source to destination."""

    # Arrange
    source: pathlib.Path
    destination: pathlib.Path
    source, destination = test_dirs
    q = Query(Suffix('txt'))
    files = list(q.files(source, recursive=True))

    # Act
    result = file_actions.copy_files(files, destination)

    # Assert
    assert result.status
    for name in ["a.txt", "b.txt", "c.txt", "d.txt"]:
        assert (destination / name).exists(), f"File {name} should exist in nested destination"

def test_move_files_flat(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test moving flat files from source to destination."""

    # Arrange
    source: pathlib.Path
    destination: pathlib.Path
    source, destination = test_dirs
    q = Query(Suffix('txt'))
    files = list(q.files(source, recursive=False))

    # Act
    result = file_actions.move_files(files, destination)

    # Assert
    assert result.status
    for name in ["a.txt", "b.txt"]:
        assert (destination / name).exists(), f"File {name} should exist in destination after move"
        assert not (source / name).exists(), f"File {name} should not exist in source after move"

def test_move_files_nested(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test moving nested files from source to destination."""

    # Arrange
    source: pathlib.Path
    destination: pathlib.Path
    source, destination = test_dirs
    q = Query(Suffix("txt") )
    files = list(q.files(source, recursive=True))

    # Act
    result = file_actions.move_files(files, destination)

    # Assert
    assert result.status
    for name in ["a.txt", "b.txt", "c.txt", "d.txt"]:
        assert (destination / name).exists(), f"File {name} should exist in destination after move"
    for sub, fname in [("sub1", "c.txt"), ("sub2", "d.txt")]:
        assert not (source / sub / fname).exists(), f"File {fname} should not exist in source after move"

def test_delete_files_flat(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test deleting flat files from source."""

    # Arrange
    source, _ = test_dirs
    q = Query(Suffix("txt") )
    files = list(q.files(source, recursive=False))

    # Act
    result = file_actions.delete_files(files)

    # Assert
    assert result.status
    for name in ["a.txt", "b.txt"]:
        assert not (source / name).exists(), f"File {name} should be deleted from source"

def test_delete_files_nested(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test deleting nested files from source."""

    # Arrange
    source, _ = test_dirs
    q = Query(Suffix("txt") )
    files = list(q.files(source, recursive=True))

    # Act
    result = file_actions.delete_files(files)

    # Assert
    assert result.status
    for name in ["a.txt", "b.txt", "c.txt", "d.txt"]:
        assert not (source / name).exists(), f"File {name} should be deleted from source"
    for sub, fname in [("sub1", "c.txt"), ("sub2", "d.txt")]:
        assert not (source / sub / fname).exists(), f"File {fname} should be deleted from sub folders source"
