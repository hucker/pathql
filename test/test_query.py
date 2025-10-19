"""
Tests for Query class and filter composition on a mini filesystem.
"""

import shutil
import pytest
from pathlib import Path
from pathql.query import Query
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.filters.type import Type


@pytest.fixture
def hundred_files(tmp_path: Path):
    """
    Create a temp folder with 100 files for benchmarking and concurrency tests.

    - Arrange: Create a temporary folder and populate it with 100 files.
    - Act: Yield the folder for use in tests.
    - Teardown: Clean up the folder after the test.
    """
    # Arrange
    folder = tmp_path / "hundred_files"
    folder.mkdir()
    for i in range(100):
        (folder / f"file_{i}.txt").write_text("x")

    # Act
    yield folder

    # Teardown
    shutil.rmtree(folder)


@pytest.fixture
def mini_fs(tmp_path: Path) -> Path:
    """
    Create a small file structure for query tests.

    - Arrange: Create a temporary folder and populate it with files and subdirectories.
    - Act: Return the temporary folder for use in tests.
    - Teardown: No explicit teardown required as tmp_path handles cleanup.
    """
    # Arrange
    f1 = tmp_path / "foo.txt"
    f2 = tmp_path / "bar.md"
    f3 = tmp_path / "baz.txt"
    d1 = tmp_path / "subdir"
    d1.mkdir()
    f4 = d1 / "qux.txt"
    f1.write_text("a" * 100)
    f2.write_text("b" * 200)
    f3.write_text("c" * 50)
    f4.write_text("d" * 300)

    # Act
    return tmp_path


def test_query_size_and_suffix(mini_fs: Path) -> None:
    """
    Test Query with size and suffix filters.

    - Arrange: Set up a mini filesystem and a Query for files with size >= 100 and suffix 'txt'.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify the matched files have the correct size and suffix.
    """
    # Arrange
    q = Query((Size() >= 100) & (Suffix == "txt"))

    # Act
    files = list(q.files(mini_fs, recursive=True, files=True, threaded=False))
    names = sorted(f.name for f in files)

    # Assert
    assert names == ["foo.txt", "qux.txt"]


def test_query_or_and(mini_fs: Path) -> None:
    """
    Test Query with OR and AND filters.

    - Arrange: Set up a mini filesystem and a Query combining size and suffix filters with OR and AND.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify the matched files meet the filter criteria.
    """
    # Arrange
    q = Query(((Size() > 250) & (Suffix == "txt")) | (Suffix == "md"))

    # Act
    files = list(q.files(mini_fs, recursive=True, files=True, threaded=False))
    names = sorted(f.name for f in files)

    # Assert
    assert names == ["bar.md", "qux.txt"]


def test_query_in_operator(mini_fs: Path) -> None:
    """
    Test Query with 'in' operator for suffix.

    - Arrange: Set up a mini filesystem and a Query for files with suffix 'txt' and size > 50.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify the matched files meet the filter criteria.
    """
    # Arrange
    q = Query((Suffix == "txt") & (Size() > 50))

    # Act
    files = list(q.files(mini_fs, recursive=True, files=True, threaded=False))

    # Assert
    for f in files:
        assert "txt" in Suffix(["txt"])
        assert f.suffix == ".txt"


def test_query_type_file_and_dir(mini_fs: Path) -> None:
    """
    Test Query for file and directory types.

    - Arrange: Set up a mini filesystem and Queries for file and directory types.
    - Act: Execute the queries to retrieve matching files and directories.
    - Assert: Verify the matched files are of type FILE and directories are of type DIRECTORY.
    """
    # Arrange
    q_files = Query(Type == Type.FILE)
    q_dirs = Query(Type == Type.DIRECTORY)

    # Act
    files = list(q_files.files(mini_fs, recursive=True, files=True, threaded=False))
    dirs = list(q_dirs.files(mini_fs, recursive=True, files=False, threaded=False))

    # Assert
    assert all(f.is_file() for f in files)
    assert all(d.is_dir() for d in dirs)


def test_query_complex(mini_fs: Path) -> None:
    """
    Test Query with complex filter combinations.

    - Arrange: Set up a mini filesystem and a Query combining multiple filters with OR and AND.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify the matched files meet the filter criteria.
    """
    # Arrange
    q = Query(((Suffix == "txt") & (Size() > 50)) | ((Suffix == "md") & (Size() < 300)))

    # Act
    files = list(q.files(mini_fs, recursive=True, files=True, threaded=False))
    names = sorted(f.name for f in files)

    # Assert
    assert names == ["bar.md", "foo.txt", "qux.txt"]


def test_threaded_vs_unthreaded_equivalence_hundred(hundred_files: Path) -> None:
    """
    Verify that threaded and unthreaded Query methods yield the same results on 100 files.

    - Arrange: Set up a folder with 100 files and a Query for files with suffix 'txt'.
    - Act: Execute the query with threaded and unthreaded methods.
    - Assert: Verify the results are identical.
    """
    # Arrange
    q = Query(Suffix == "txt")

    # Act
    threaded = set(f.name for f in q.files(hundred_files, recursive=True, files=True, threaded=True))
    unthreaded = set(f.name for f in q.files(hundred_files, recursive=True, files=True, threaded=False))

    # Assert
    assert threaded == unthreaded
    assert len(threaded) == 100



