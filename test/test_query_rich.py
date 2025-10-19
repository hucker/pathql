"""Tests for Query on a rich filesystem, including size, suffix, stem, age, and type filters."""

from typing import Tuple
from pathlib import Path
from pathql.query import Query
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.filters.stem import Stem
from pathql.filters.age import AgeMinutes
from pathql.filters.type import Type


def test_all_files_bigger_than_50(rich_filesystem: Tuple[str, float]) -> None:
    """
    Test files with size greater than 50.

    - Arrange: Set up a rich filesystem and a Query for files larger than 50.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify all matched files have size > 50.
    """
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    q = Query(Size() > 50)

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now))

    # Assert
    assert all(f.stat().st_size > 50 for f in files)
    for f in files:
        print(f"Matched: {f} size={f.stat().st_size}")


def test_txt_files_older_than_20_seconds(rich_filesystem: Tuple[str, float]) -> None:
    """
    Test .txt files older than 20 seconds.

    - Arrange: Set up a rich filesystem and a Query for .txt files older than 20 seconds.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify all matched files are .txt and older than 20 seconds.
    """
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    q = Query((Suffix == "txt") & (AgeMinutes() > (20/60)))

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now))

    # Assert
    for f in files:
        assert f.suffix == ".txt"
        age_sec = now - f.stat().st_mtime
        assert age_sec > 20


def test_bmp_files_size_and_age(rich_filesystem: Tuple[str, float]) -> None:
    """
    Test .bmp files with size > 30 and age > 0.01 minutes.

    - Arrange: Set up a rich filesystem and a Query for .bmp files with specific size and age.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify all matched files are .bmp, size > 30, and age > 0.01 minutes.
    """
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    q = Query((Suffix == "bmp") & (Size() > 30) & (AgeMinutes() > 0.01))

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now))

    # Assert
    for f in files:
        assert f.suffix == ".bmp"
        assert f.stat().st_size > 30
        assert (now - f.stat().st_mtime) > 0.01 * 60


def test_stem_pattern_and_type(rich_filesystem: Tuple[str, float]) -> None:
    """
    Test files with stem starting with 'g' and are regular files.

    - Arrange: Set up a rich filesystem and a Query for files with specific stem pattern and type.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify all matched files have stem starting with 'g' and are regular files.
    """
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    q = Query((Stem(r"^g.*") & (Type == Type.FILE)))

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now))

    # Assert
    for f in files:
        assert f.stem.startswith("g")
        assert f.is_file()


def test_complex_combination(rich_filesystem: Tuple[str, float]) -> None:
    """
    Test .txt files with size > 20, older than 10 seconds, and stem containing 'd'.

    - Arrange: Set up a rich filesystem and a Query for .txt files with specific size, age, and stem pattern.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify all matched files meet the criteria.
    """
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    q = Query((Suffix == "txt") & (Size() > 20) & (AgeMinutes() > (10/60)) & Stem(r"d"))

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now))

    # Assert
    for f in files:
        assert f.suffix == ".txt"
        assert f.stat().st_size > 20
        assert (now - f.stat().st_mtime) > 10
        assert "d" in f.stem


def test_all_files_type_file(rich_filesystem: Tuple[str, float]) -> None:
    """
    Test all files of type FILE.

    - Arrange: Set up a rich filesystem and a Query for files of type FILE.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify all matched files are of type FILE.
    """
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    q = Query(Type == Type.FILE)

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now))

    # Assert
    for f in files:
        assert f.is_file()


def test_all_files_type_directory(rich_filesystem: Tuple[str, float]) -> None:
    """
    Test all files of type DIRECTORY.

    - Arrange: Set up a rich filesystem and a Query for files of type DIRECTORY.
    - Act: Execute the query to retrieve matching files.
    - Assert: Verify all matched files are of type DIRECTORY.
    """
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    q = Query(Type == Type.DIRECTORY)

    # Act
    files = list(q.files(root_path, recursive=True, files=False, now=now))

    # Assert
    for f in files:
        assert f.is_dir()
