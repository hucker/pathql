import pathlib
import zipfile

import pytest

from pathql.actions import file_actions
from pathql.actions import zip as zip_actions
from pathql.actions.zip import (
    zip_copy_files,
    zip_delete_files,
    zip_files,
    zip_move_files,
)
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
def sample_files(tmp_path: pathlib.Path) -> list[pathlib.Path]:
    """Create sample files for zipping."""
    files: list[pathlib.Path] = []
    for name in ["a.txt", "b.txt"]:
        f = tmp_path / name
        f.write_text(f"content-{name}")
        files.append(f)
    return files


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
    files = Query(where_expr=Suffix("txt")).select(source, recursive=False)
    target_zip = destination / "flat_nostructure.zip"
    # Act
    result = zip_actions.zip_files(
        files, target_zip, preserve_dir_structure=False, root=source
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
    files = Query(where_expr=Suffix("txt")).select(source, recursive=False)
    target_zip = destination / "flat_structure.zip"
    # Act
    result = zip_actions.zip_files(
        files, target_zip, preserve_dir_structure=True, root=source
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
    files = Query(where_expr=Suffix("txt")).select(source, recursive=True)
    target_zip = destination / "nested_nostructure.zip"
    # Act
    result = zip_actions.zip_files(
        files, target_zip, preserve_dir_structure=False, root=source
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
    files = Query(where_expr=Suffix("txt")).select(source, recursive=True)
    target_zip = destination / "nested_structure.zip"
    # Act
    result = zip_actions.zip_files(
        files, target_zip, preserve_dir_structure=True, root=source
    )
    # Assert
    assert result.status
    with zipfile.ZipFile(target_zip) as zf:
        names = zf.namelist()
        assert "a.txt" in names
        assert "b.txt" in names
        assert "sub1/c.txt" in names
        assert "sub2/d.txt" in names


@pytest.mark.parametrize(
    "copy_func", [file_actions.copy_files, file_actions.fast_copy_files]
)
def test_copy_files_flat(test_dirs: tuple[pathlib.Path, pathlib.Path], copy_func):
    """Test copying flat files from source to destination using copy_func."""
    # Arrange
    source, destination = test_dirs
    q = Query(where_expr=Suffix("txt"))
    files = list(q.files(source, recursive=False))

    # Act
    result = copy_func(files, destination)

    # Assert
    assert result.status, "Copy operation should report success"
    for name in ["a.txt", "b.txt"]:
        assert (destination / name).exists(), (
            f"File {name} should exist in flat destination after copy"
        )


@pytest.mark.parametrize(
    "copy_func", [file_actions.copy_files, file_actions.fast_copy_files]
)
def test_copy_files_nested(test_dirs: tuple[pathlib.Path, pathlib.Path], copy_func):
    """Test copying nested files from source to destination using copy_func."""
    # Arrange
    source, destination = test_dirs
    q = Query(where_expr=Suffix("txt"))
    files = list(q.files(source, recursive=True))

    # Act
    result = copy_func(files, destination)

    # Assert
    assert result.status, "Copy operation should report success"
    for name in ["a.txt", "b.txt", "c.txt", "d.txt"]:
        assert (destination / name).exists(), (
            f"File {name} should exist in nested destination after copy"
        )


def test_move_files_flat(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test moving flat files from source to destination."""
    # Arrange
    source, destination = test_dirs
    q = Query(where_expr=Suffix("txt"))
    files = list(q.files(source, recursive=False))

    # Act
    result = file_actions.move_files(files, destination)

    # Assert
    assert result.status, "Move operation should report success"
    for name in ["a.txt", "b.txt"]:
        assert (destination / name).exists(), (
            f"File {name} should exist in destination after move"
        )
        assert not (source / name).exists(), (
            f"File {name} should not exist in source after move"
        )


def test_move_files_nested(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test moving nested files from source to destination."""
    # Arrange
    source, destination = test_dirs
    q = Query(where_expr=Suffix("txt"))
    files = list(q.files(source, recursive=True))

    # Act
    result = file_actions.move_files(files, destination)

    # Assert
    assert result.status, "Move operation should report success"
    for name in ["a.txt", "b.txt", "c.txt", "d.txt"]:
        assert (destination / name).exists(), (
            f"File {name} should exist in destination after move"
        )
    for sub, fname in [("sub1", "c.txt"), ("sub2", "d.txt")]:
        assert not (source / sub / fname).exists(), (
            f"File {fname} should not exist in source after move"
        )


def test_delete_files_flat(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test deleting flat files from source."""
    # Arrange
    source, _ = test_dirs
    q = Query(where_expr=Suffix("txt"))
    files = list(q.files(source, recursive=False))

    # Act
    result = file_actions.delete_files(files)

    # Assert
    assert result.status, "Delete operation should report success"
    for name in ["a.txt", "b.txt"]:
        assert not (source / name).exists(), (
            f"File {name} should be deleted from source"
        )


def test_delete_files_nested(test_dirs: tuple[pathlib.Path, pathlib.Path]):
    """Test deleting nested files from source."""
    # Arrange
    source, _ = test_dirs
    q = Query(where_expr=Suffix("txt"))
    files = list(q.files(source, recursive=True))

    # Act
    result = file_actions.delete_files(files)

    # Assert
    assert result.status, "Delete operation should report success"
    for name in ["a.txt", "b.txt", "c.txt", "d.txt"]:
        assert not (source / name).exists(), (
            f"File {name} should be deleted from source"
        )
    for sub, fname in [("sub1", "c.txt"), ("sub2", "d.txt")]:
        assert not (source / sub / fname).exists(), (
            f"File {fname} should be deleted from sub folders source"
        )


def test_zip_files_flat(sample_files, tmp_path: pathlib.Path):
    """Test zip_files with flat structure."""
    # Arrange
    target_zip: pathlib.Path = tmp_path / "flat.zip"
    # Act
    result = zip_files(sample_files, target_zip, preserve_dir_structure=False)
    # Assert
    assert result.status
    with zipfile.ZipFile(target_zip) as zf:
        names = zf.namelist()
        for f in sample_files:
            assert f.name in names


def test_zip_files_structure(sample_files, tmp_path: pathlib.Path):
    """Test zip_files with directory structure preserved."""
    # Arrange
    target_zip: pathlib.Path = tmp_path / "structure.zip"
    root: pathlib.Path = tmp_path
    # Act
    result = zip_files(sample_files, target_zip, preserve_dir_structure=True, root=root)
    # Assert
    assert result.status
    with zipfile.ZipFile(target_zip) as zf:
        names = zf.namelist()
        for f in sample_files:
            assert f.name in names  # Since files are at root


def test_zip_delete_files(sample_files, tmp_path: pathlib.Path):
    """Test zip_delete_files deletes files after zipping."""
    # Arrange
    target_zip: pathlib.Path = tmp_path / "delete.zip"
    files: pathlib.Path = list(sample_files)
    # Act
    result = zip_delete_files(files, target_zip)
    # Assert
    assert result.status
    for f in files:
        assert not f.exists(), f"{f} should be deleted"
    with zipfile.ZipFile(target_zip) as zf:
        for f in files:
            assert f.name in zf.namelist()


def test_zip_move_files(sample_files, tmp_path: pathlib.Path):
    """Test zip_move_files moves files after zipping."""
    # Arrange
    target_zip = tmp_path / "move.zip"
    move_target = tmp_path / "moved"
    move_target.mkdir()
    files: pathlib.Path = list(sample_files)
    # Act
    result: pathlib.Path = zip_move_files(files, target_zip, move_target)
    # Assert
    assert result.status
    for f in files:
        moved_file = move_target / f.name
        assert moved_file.exists(), f"{moved_file} should exist in move_target"
        assert not f.exists(), f"{f} should not exist in original location"
    with zipfile.ZipFile(target_zip) as zf:
        for f in files:
            assert f.name in zf.namelist()


def test_zip_copy_files(sample_files, tmp_path: pathlib.Path):
    """Test zip_copy_files copies files after zipping."""
    # Arrange
    target_zip: pathlib.Path = tmp_path / "copy.zip"
    copy_target: pathlib.Path = tmp_path / "copied"
    copy_target.mkdir()
    files = list(sample_files)
    # Act
    result = zip_copy_files(files, target_zip, copy_target)
    # Assert
    assert result.status
    for f in files:
        copied_file = copy_target / f.name
        assert copied_file.exists(), f"{copied_file} should exist in copy_target"
        assert f.exists(), f"{f} should still exist in original location"
    with zipfile.ZipFile(target_zip) as zf:
        for f in files:
            assert f.name in zf.namelist()


def test_zip_files_error(tmp_path: pathlib.Path):
    """Test zip_files with a missing file (error case)."""
    # Arrange
    target_zip: pathlib.Path = tmp_path / "error.zip"
    missing_file: pathlib.Path = tmp_path / "missing.txt"
    # Act
    result = zip_files([missing_file], target_zip)
    # Assert
    assert not result.status
    assert missing_file in result.failed
    assert missing_file in result.errors
    assert missing_file in result.errors
    assert missing_file in result.errors
