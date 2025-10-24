"""Query tests on a richer filesystem (size, suffix, stem, age, type)."""

import datetime as dt
from pathlib import Path
from typing import Tuple

from pathql.filters.age import AgeSeconds
from pathql.filters.size import Size
from pathql.filters.stem import Stem
from pathql.filters.suffix import Suffix
from pathql.filters.file_type import FileType
from pathql.query import Query


def test_all_files_bigger_than_50(
    rich_filesystem: Tuple[str, float],
) -> None:
    """All matched files have size greater than 50."""
    # Arrange
    root, now = rich_filesystem
    now_dt = dt.datetime.fromtimestamp(now)
    root_path = Path(root)
    q = Query(Size() > 50)

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now_dt))

    # Assert
    assert all(f.stat().st_size > 50 for f in files)
    for f in files:
        print(f"Matched: {f} size={f.stat().st_size}")


def test_txt_files_older_than_20_seconds(
    rich_filesystem: Tuple[str, float],
) -> None:
    """Matched .txt files are older than 20 seconds."""
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    now_dt = dt.datetime.fromtimestamp(now)
    q = Query(Suffix('txt') & (AgeSeconds() > 20))

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now_dt))

    # Assert
    for f in files:
        assert f.suffix == ".txt"
        age_sec = now - f.stat().st_mtime
        assert age_sec > 20


def test_bmp_files_size_and_age(
    rich_filesystem: Tuple[str, float],
) -> None:
    """Matched .bmp files have size>30 and age>0.01 minutes."""
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    now_dt = dt.datetime.fromtimestamp(now)
    q = Query(Suffix("bmp")  & (Size() > 30) & (AgeSeconds() > 1))

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now_dt))

    # Assert
    for f in files:
        assert f.suffix == ".bmp"
        assert f.stat().st_size > 30
        assert (now - f.stat().st_mtime) > 0.01 * 60


def test_stem_pattern_and_type(
    rich_filesystem: Tuple[str, float],
) -> None:
    """Files with stem starting with 'g' are regular files."""
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    now_dt = dt.datetime.fromtimestamp(now)
    q = Query((Stem(r"^g.*") & (FileType().file)))

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now_dt))

    # Assert
    for f in files:
        assert f.stem.startswith("g")
        assert f.is_file()


def test_complex_combination(
    rich_filesystem: Tuple[str, float],
) -> None:
    """Complex filter combination matches the expected files."""
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    now_dt = dt.datetime.fromtimestamp(now)
    q = Query(Suffix("txt") & (Size() > 20) & (AgeSeconds() > 10) & Stem(r"d"))

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now_dt))

    # Assert
    for f in files:
        assert f.suffix == ".txt"
        assert f.stat().st_size > 20
        assert (now - f.stat().st_mtime) > 10
        assert "d" in f.stem


def test_all_files_type_file(
    rich_filesystem: Tuple[str, float],
) -> None:
    """All matched files are of type FILE."""
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    now_dt = dt.datetime.fromtimestamp(now)
    q = Query(FileType().file)

    # Act
    files = list(q.files(root_path, recursive=True, files=True, now=now_dt))

    # Assert
    for f in files:
        assert f.is_file()


def test_all_files_type_directory(
    rich_filesystem: Tuple[str, float],
) -> None:
    """All matched entries are directories when files=False is used."""
    # Arrange
    root, now = rich_filesystem
    root_path = Path(root)
    now_dt = dt.datetime.fromtimestamp(now)
    q = Query(FileType().directory)

    # Act
    files = list(q.files(root_path, recursive=True, files=False, now=now_dt))

    # Assert
    for f in files:
        assert f.is_dir()
