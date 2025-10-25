"""
Test Query.select with multiple folders.

This module verifies that Query.select can accept a list of folders and return all matching files from each folder. Uses AAA (Arrange-Act-Assert) comments and explicit actual/expected naming in assertions.
"""
import pathlib

import pytest

from pathql.query import MatchAll, Query


@pytest.fixture
def multi_folder_fixture(tmp_path: pathlib.Path) -> list[pathlib.Path]:
    # Arrange: Create three explicit folders with files
    """
    Create three explicit folders (alpha, beta, gamma) each with two files.
    Returns a list of folder paths.
    """
    # AAA: Arrange
    folder_names = ["alpha", "beta", "gamma"]
    folders = []
    for name in folder_names:
        folder = tmp_path / name
        folder.mkdir()
        for j in range(2):
            file = folder / f"file_{j}.txt"
            file.write_text(f"content {name}-{j}")
        folders.append(folder)
    return folders

@pytest.mark.parametrize("folder_combo", [
    (["alpha"],),
    (["beta"],),
    (["gamma"],),
    (["alpha", "beta"],),
    (["beta", "gamma"],),
    (["alpha", "gamma"],),
    (["alpha", "beta", "gamma"],),
])
def test_query_select_multi_folder(
    multi_folder_fixture: list[pathlib.Path],
    folder_combo: tuple[list[str]]
) -> None:
    """
    Test that Query.select returns all files from the specified folders.
    """
    # Arrange
    folder_names = ["alpha", "beta", "gamma"]
    name_to_folder = {name: folder for name, folder in zip(folder_names, multi_folder_fixture)}
    selected_folders = [name_to_folder[name] for name in folder_combo[0]]

    # Act
    q = Query(MatchAll())
    result = q.select(selected_folders, recursive=False, files=True)
    actual_files = list(result)

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
            f"File {f} not in selected folders {selected_folders}"
        )
