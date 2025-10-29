"""
Test Query.files with multiple folders.

This module verifies that Query.files can accept a list of folders and yield all matching files from each folder.
Follows AAA (Arrange-Act-Assert) conventions, uses explicit actual/expected naming, and includes type hints and docstrings.
"""

import pathlib

import pytest

from pathql.query import AllowAll, Query


@pytest.fixture
def multi_folder_fixture(tmp_path: pathlib.Path) -> list[pathlib.Path]:
    """
    Create three explicit folders (alpha, beta, gamma) each with two files.
    Returns a list of folder paths.
    """
    # Arrange
    folder_names = ["alpha", "beta", "gamma"]
    folders: list[pathlib.Path] = []
    for name in folder_names:
        folder = tmp_path / name
        folder.mkdir()
        for j in range(2):
            file = folder / f"file_{j}.txt"
            file.write_text(f"content {name}-{j}")
        folders.append(folder)
    return folders


@pytest.mark.parametrize(
    "folder_combo",
    [
        ["alpha"],
        ["beta"],
        ["gamma"],
        ["alpha", "beta"],
        ["beta", "gamma"],
        ["alpha", "gamma"],
        ["alpha", "beta", "gamma"],
    ],
)
def test_query_files_multi_folder(
    multi_folder_fixture: list[pathlib.Path], folder_combo: list[str]
) -> None:
    """
    Test that Query.files yields all files from the specified folders.
    Uses AAA (Arrange-Act-Assert) and explicit actual/expected naming.
    """
    # Arrange
    folder_names = ["alpha", "beta", "gamma"]
    name_to_folder = {
        name: folder for name, folder in zip(folder_names, multi_folder_fixture)
    }
    selected_folders: list[pathlib.Path] = [
        name_to_folder[name] for name in folder_combo
    ]

    # Act
    query = Query(where_expr=AllowAll())
    actual_files = list(
        query.files(from_paths=selected_folders, recursive=False, files_only=True)
    )

    # Assert
    expected_count = 2 * len(selected_folders)
    actual_count = len(actual_files)
    assert actual_count == expected_count, (
        f"Expected {expected_count} files, got {actual_count} for folders {folder_combo}"
    )
    for f in actual_files:
        assert any(str(f).startswith(str(folder)) for folder in selected_folders), (
            f"File {f} not in selected folders {selected_folders}"
        )
