"""Tests for Query class and filter composition on a mini filesystem."""

import pathlib
import shutil

import pytest

from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.filters.file_type import FileType
from pathql.query import Query


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
    ]
)
def test_query_no_filter_param(mini_fs: pathlib.Path, recursive: bool, expected_files: set[str]) -> None:
    """Test Query with no filter (matches all files), both recursive and non-recursive."""
    # Arrange
    q = Query()
    # Act
    files = q.select(mini_fs, recursive=recursive, files=True, threaded=False)
    actual_files = set(f.name for f in files)
    # Assert
    assert actual_files == expected_files

def test_query_size_and_suffix(mini_fs: pathlib.Path) -> None:
    """Test Query with size and suffix filters."""
    # Arrange
    q = Query((Size() >= 100) & Suffix("txt"))
    # Act
    files = list(q.files(mini_fs, recursive=True, files=True, threaded=False))
    names = sorted(f.name for f in files)
    # Assert
    assert names == ["foo.txt", "qux.txt"]


def test_query_or_and(mini_fs: pathlib.Path) -> None:
    """Test Query with OR and AND filters."""
    # Arrange
    q = Query((Size() > 250) & Suffix("txt")  | Suffix("md"))
    # Act
    files = list(q.files(mini_fs, recursive=True, files=True, threaded=False))
    names = sorted(f.name for f in files)
    # Assert
    assert names == ["bar.md", "qux.txt"]




def test_query_type_file_and_dir(mini_fs: pathlib.Path) -> None:
    """Test Query for file and directory types."""
    # Arrange
    q_files = Query(FileType().file)
    q_dirs = Query(FileType().directory)
    # Act
    files = list(q_files.files(mini_fs, recursive=True, files=True, threaded=False))
    dirs = list(q_dirs.files(mini_fs, recursive=True, files=False, threaded=False))
    # Assert
    assert all(f.is_file() for f in files)
    assert all(d.is_dir() for d in dirs)


def test_query_complex(mini_fs: pathlib.Path) -> None:
    """Test Query with complex filter combinations."""
    # Arrange
    q = Query((Suffix("txt") & (Size() > 50)) | (Suffix("md")  & (Size() < 300)))

    # Act
    files = list(q.files(mini_fs, recursive=True, files=True, threaded=False))
    names = sorted(f.name for f in files)

    # Assert
    assert names == ["bar.md", "foo.txt", "qux.txt"]


def test_threaded_vs_unthreaded_equivalence_hundred(
    hundred_files: pathlib.Path,
) -> None:
    """Threaded and unthreaded Query yield the same results on 100 files."""
    # Arrange
    q = Query(Suffix("txt"))

    # Act
    threaded = set(
        f.name
        for f in q.files(
            hundred_files,
            recursive=True,
            files=True,
            threaded=True,
        )
    )
    unthreaded = set(
        f.name
        for f in q.files(
            hundred_files,
            recursive=True,
            files=True,
            threaded=False,
        )
    )

    # Assert
    assert threaded == unthreaded
    assert len(threaded) == 100
    assert threaded == unthreaded
    assert len(threaded) == 100
