import pathlib
import zipfile

import pytest

from pathql.actions import zip as zip_actions
from pathql.filters import Suffix
from pathql.query import Query

TREE = {
    "src": [
        "a.txt",
        "b.txt",
        {"sub1": ["c.txt"]},
        {"sub2": ["d.txt"]},
    ]
}


def create_tree(base: pathlib.Path, tree: dict):
    for folder, items in tree.items():
        folder_path = base / folder
        folder_path.mkdir()
        for item in items:
            if isinstance(item, str):
                (folder_path / item).write_text(
                    item[0]
                )  # Write first letter as content
            elif isinstance(item, dict):
                create_tree(folder_path, item)


@pytest.fixture
def test_dirs(tmp_path) -> tuple[pathlib.Path, pathlib.Path]:
    create_tree(tmp_path, TREE)
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    dst.mkdir()
    return src, dst


def test_zip_files_flat_no_structure(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test zipping flat files from source without preserving structure."""
    # Arrange
    source, destination = test_dirs
    files = Query(Suffix("txt")).select(source, recursive=False)
    target_zip = destination / "flat_nostructure.zip"
    # Act
    result = zip_actions.zip_files(
        files, source, target_zip, preserve_dir_structure=False
    )
    # Assert
    assert result.status
    with zipfile.ZipFile(target_zip) as zf:
        names = zf.namelist()
        assert "a.txt" in names
        assert "b.txt" in names
        assert "c.txt" not in names
        assert "d.txt" not in names


def test_zip_files_flat_with_structure(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test zipping flat files from source with preserving structure (should be same as no structure for flat)."""
    # Arrange
    source, destination = test_dirs
    files = Query(Suffix("txt")).select(source, recursive=False)
    target_zip = destination / "flat_structure.zip"
    # Act
    result = zip_actions.zip_files(
        files, source, target_zip, preserve_dir_structure=True
    )
    # Assert
    assert result.status
    with zipfile.ZipFile(target_zip) as zf:
        names = zf.namelist()
        assert "a.txt" in names
        assert "b.txt" in names
        assert "c.txt" not in names
        assert "d.txt" not in names


def test_zip_files_nested_no_structure(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test zipping nested files from source without preserving structure."""
    # Arrange
    source, destination = test_dirs
    files = Query(Suffix("txt")).select(source, recursive=True)
    target_zip = destination / "nested_nostructure.zip"
    # Act
    result = zip_actions.zip_files(
        files, source, target_zip, preserve_dir_structure=False
    )
    # Assert
    assert result.status
    with zipfile.ZipFile(target_zip) as zf:
        names = zf.namelist()
        # All files should be at the root of the zip
        assert "a.txt" in names
        assert "b.txt" in names
        assert "c.txt" in names
        assert "d.txt" in names
        assert not any("sub1/c.txt" in n or "sub2/d.txt" in n for n in names)


def test_zip_files_nested_with_structure(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test zipping nested files from source with preserving structure."""
    # Arrange
    source, destination = test_dirs
    files = Query(Suffix("txt")).select(source, recursive=True)
    target_zip = destination / "nested_structure.zip"
    # Act
    result = zip_actions.zip_files(
        files, source, target_zip, preserve_dir_structure=True
    )
    # Assert
    assert result.status
    with zipfile.ZipFile(target_zip) as zf:
        names = zf.namelist()
        assert "a.txt" in names
        assert "b.txt" in names
        assert "sub1/c.txt" in names
        assert "sub2/d.txt" in names
