"""
Tests for Query class and filter composition on a mini filesystem.
Demonstrates Query initialization and method usage with from_path,
including support for single path, list, pathlib.Path, and glob patterns.
"""

import pathlib
import shutil

import pytest

from pathql.filters.base import AllowAll
from pathql.filters.file_type import FileType
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.query import Query


def test_query_select_list_of_paths(mini_fs: pathlib.Path) -> None:
    """Test Query.select() with a list of paths."""
    subdir = mini_fs / "subdir"
    paths = [mini_fs, subdir]
    q = Query(where_expr=Suffix(".txt"))
    files = sorted([p.name for p in q.select(paths)])
    assert set(files) == {"foo.txt", "baz.txt", "qux.txt"}


def test_query_files_subdir(mini_fs: pathlib.Path) -> None:
    """Test Query.files() with a subdirectory path."""
    subdir = mini_fs / "subdir"
    q = Query(where_expr=Suffix(".txt"))
    files = sorted([p.name for p in q.files(subdir)])
    assert files == ["qux.txt"]


def test_query_select_subdir(mini_fs: pathlib.Path) -> None:
    """Test Query.select() with a subdirectory path."""
    subdir = mini_fs / "subdir"
    q = Query(where_expr=Suffix(".txt"))
    files = sorted([p.name for p in q.select(subdir)])
    assert files == ["qux.txt"]


@pytest.fixture(name="hundred_files")
def _hundred_files(tmp_path: pathlib.Path):  # pyright: ignore[reportUnusedFunction]
    """Create a temp folder with 100 files for benchmarking/concurrency tests."""
    # Arrange
    folder = tmp_path / "hundred_files"
    folder.mkdir()
    for i in range(100):
        (folder / f"file_{i}.txt").write_text("x")
    yield folder
    # Teardown
    shutil.rmtree(folder)


@pytest.fixture(name="mini_fs")
def _mini_fs(tmp_path: pathlib.Path) -> pathlib.Path:  # pyright: ignore[reportUnusedFunction]
    """Create a small file structure for query tests."""
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
    return tmp_path


@pytest.mark.parametrize(
    "recursive,expected_files",
    [
        (True, set(["foo.txt", "bar.md", "baz.txt", "qux.txt"])),
        (False, set(["foo.txt", "bar.md", "baz.txt"])),
    ],
)
def test_query_no_filter_param(
    mini_fs: pathlib.Path, recursive: bool, expected_files: set[str]
) -> None:
    """Test Query with no filter (matches all files), both recursive and non-recursive."""
    # Arrange
    q = Query()
    # Act
    files = q.select(mini_fs, recursive=recursive, files_only=True, threaded=False)
    actual_files = set(f.name for f in files)
    # Assert
    assert actual_files == expected_files


def test_query_size_and_suffix(mini_fs: pathlib.Path) -> None:
    """Test Query with size and suffix filters."""
    # Arrange
    q = Query(where_expr=(Size() >= 100) & Suffix("txt"))
    # Act
    files = list(q.files(mini_fs, recursive=True, files_only=True, threaded=False))
    names = sorted(f.name for f in files)
    # Assert
    assert names == ["foo.txt", "qux.txt"]


def test_query_or_and(mini_fs: pathlib.Path) -> None:
    """Test Query with OR and AND filters."""
    # Arrange
    q = Query(where_expr=(Size() > 250) & Suffix("txt") | Suffix("md"))
    # Act
    files = list(q.files(mini_fs, recursive=True, files_only=True, threaded=False))
    names = sorted(f.name for f in files)
    # Assert
    assert names == ["bar.md", "qux.txt"]


def test_query_select_tuple_and_nested_tuple(mini_fs: pathlib.Path) -> None:
    """Test Query.select() with tuple and nested tuple of paths."""
    subdir = mini_fs / "subdir"
    paths = (mini_fs, subdir)
    q = Query(where_expr=Suffix(".txt"))
    files = sorted([p.name for p in q.select(paths)])
    # Should find all .txt files in both mini_fs and subdir
    assert set(files) == {"foo.txt", "baz.txt", "qux.txt"}


def test_query_type_file_and_dir(mini_fs: pathlib.Path) -> None:
    """Test Query for file and directory types."""
    # Arrange
    q_files = Query(where_expr=FileType().file)
    q_dirs = Query(where_expr=FileType().directory)
    # Act
    files = list(
        q_files.files(mini_fs, recursive=True, files_only=True, threaded=False)
    )
    dirs = list(q_dirs.files(mini_fs, recursive=True, files_only=False, threaded=False))
    # Assert
    assert all(f.is_file() for f in files)
    assert all(d.is_dir() for d in dirs)


def test_query_complex(mini_fs: pathlib.Path) -> None:
    """Test Query with complex filter combinations."""
    # Arrange
    q = Query(
        where_expr=(Suffix("txt") & (Size() > 50)) | (Suffix("md") & (Size() < 300))
    )

    # Act
    files = list(q.files(mini_fs, recursive=True, files_only=True, threaded=False))
    names = sorted(f.name for f in files)

    # Assert
    assert names == ["bar.md", "foo.txt", "qux.txt"]


# pytest.mark.timeout(10)
def test_threaded_vs_unthreaded_equivalence_hundred(
    hundred_files: pathlib.Path,
) -> None:
    """Threaded and unthreaded Query yield the same results on 100 files."""
    # Arrange
    q = Query(where_expr=Suffix("txt"))

    # Act
    threaded = set(
        f.name
        for f in q.files(
            hundred_files,
            recursive=True,
            files_only=True,
            threaded=True,
        )
    )
    unthreaded = set(
        f.name
        for f in q.files(
            hundred_files,
            recursive=True,
            files_only=True,
            threaded=False,
        )
    )

    # Assert
    assert threaded == unthreaded
    assert len(threaded) == 100
    assert threaded == unthreaded
    assert len(threaded) == 100
    assert threaded == unthreaded
    assert len(threaded) == 100
    assert threaded == unthreaded
    assert len(threaded) == 100


def test_query_where_expr_and_from_path(tmp_path: pathlib.Path) -> None:
    """Test Query's where_expr and from_path keyword arguments."""
    # Arrange
    test_dir: pathlib.Path = tmp_path / "test_dir"
    test_dir.mkdir()
    file1: pathlib.Path = test_dir / "file1.txt"
    file2: pathlib.Path = test_dir / "file2.log"
    file1.write_text("hello")
    file2.write_text("world")

    # Act
    q: Query = Query(where_expr=Suffix(".txt"), from_paths=str(test_dir))
    results = list(q.files())


    # Assert
    assert file1 in results
    assert file2 not in results

    # Act (override from_path)
    q2: Query = Query(where_expr=AllowAll(), from_paths=str(test_dir))
    results2 = list(q2.files(from_paths=str(test_dir)))

    # Assert
    assert file1 in results2 and file2 in results2
    assert file1 in results2 and file2 in results2


def test_query_files_override_defaults(tmp_path:pathlib.Path):
    # Arrange: create files
    file1 = tmp_path / "file1.txt"
    file1.write_text("data")
    file2 = tmp_path / "file2.txt"
    file2.write_text("data")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    file3 = subdir / "file3.txt"
    file3.write_text("data")

    # Set defaults: recursive=False, so only top-level files should be found
    q = Query(where_expr=AllowAll(), from_paths=tmp_path, recursive=False, files_only=True)
    files_default = list(q.files())
    assert file1 in files_default and file2 in files_default
    assert file3 not in files_default  # Should not find file3.txt in subdir

    # Override: recursive=True, should find file3.txt as well
    files_override = list(q.files(recursive=True))
    assert file1 in files_override and file2 in files_override and file3 in files_override

def test_query_select_override_defaults(tmp_path:pathlib.Path):
    # Arrange: create files
    file1 = tmp_path / "file1.txt"
    file1.write_text("data")
    file2 = tmp_path / "file2.txt"
    file2.write_text("data")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    file3 = subdir / "file3.txt"
    file3.write_text("data")

    # Set defaults: files_only=False, so should find directories too
    q = Query(where_expr=AllowAll(), from_paths=tmp_path, files_only=False)
    files_default = list(q.select())
    assert subdir in files_default  # Should find the directory

    # Override: files_only=True and recursive=False, should not find directories or subdir files
    files_override = list(q.select(files_only=True, recursive=False))
    assert subdir not in files_override
    assert file1 in files_override and file2 in files_override and file3 not in files_override