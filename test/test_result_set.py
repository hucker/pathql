"""Tests for ResultSet aggregations (min/max/top_n/sort/average/median/count)."""

import pathlib

import pytest

from pathql.filters.suffix import Suffix
from pathql.query import Query
from pathql.result_set import ResultField, ResultSet


@pytest.mark.usefixtures("test_result_files")
def test_max_size(test_result_files: list[pathlib.Path]) -> None:
    """Test max aggregation by file size."""
    # Arrange
    result = ResultSet(test_result_files)
    expected = 3000
    # Act
    actual = result.max(ResultField.SIZE)
    # Assert
    assert actual == expected, f"Max size should be {expected}, got {actual}"


@pytest.mark.usefixtures("test_result_files")
def test_min_size(test_result_files: list[pathlib.Path]) -> None:
    """Test min aggregation by file size."""
    # Arrange
    result = ResultSet(test_result_files)
    expected = 10
    # Act
    actual = result.min(ResultField.SIZE)
    # Assert
    assert actual == expected, f"Min size should be {expected}, got {actual}"


@pytest.mark.usefixtures("test_result_files")
def test_top3_largest(test_result_files: list[pathlib.Path]) -> None:
    """Test top_n aggregation for largest files by size."""
    # Arrange
    result = ResultSet(test_result_files)
    expected = {"largest_1.txt", "largest_2.txt", "largest_3.txt"}
    # Act
    actual = {p.name for p in result.top_n(ResultField.SIZE, 3)}
    # Assert
    assert actual == expected, f"Top 3 largest files should be {expected}, got {actual}"


@pytest.mark.usefixtures("test_result_files")
def test_bottom3_smallest(test_result_files: list[pathlib.Path]) -> None:
    """Test bottom_n aggregation for smallest files by size."""
    # Arrange
    result = ResultSet(test_result_files)
    expected = {"smallest_1.txt", "smallest_2.txt", "smallest_3.txt"}
    # Act
    actual = {p.name for p in result.bottom_n(ResultField.SIZE, 3)}
    # Assert
    assert actual == expected, (
        f"Bottom 3 smallest files should be {expected}, got {actual}"
    )


@pytest.mark.usefixtures("test_result_files")
def test_sort_by_name(test_result_files: list[pathlib.Path]) -> None:
    """Test sorting files by name."""
    # Arrange
    result = ResultSet(test_result_files)
    expected_first = "a_first.txt"
    expected_last = "z_last.txt"
    # Act
    sorted_names = [p.name for p in result.sort_(ResultField.NAME)]
    # Assert
    actual_first = sorted_names[0]
    actual_last = sorted_names[-1]
    assert actual_first == expected_first, (
        f"First file by name should be '{expected_first}', got {actual_first}"
    )
    assert actual_last == expected_last, (
        f"Last file by name should be '{expected_last}', got {actual_last}"
    )


@pytest.mark.usefixtures("test_result_files")
def test_average_size(test_result_files: list[pathlib.Path]) -> None:
    """Test average aggregation by file size."""
    # Arrange
    result = ResultSet(test_result_files)
    expected = sum(p.stat().st_size for p in result) / len(result)
    # Act
    actual = result.average(ResultField.SIZE)
    # Assert
    assert actual == expected, f"Average size should be {expected}, got {actual}"


@pytest.mark.usefixtures("test_result_files")
def test_median_size(test_result_files: list[pathlib.Path]) -> None:
    """Test median aggregation by file size."""
    # Arrange
    result = ResultSet(test_result_files)
    sizes = sorted(p.stat().st_size for p in result)
    n = len(sizes)
    expected = sizes[n // 2] if n % 2 else (sizes[n // 2 - 1] + sizes[n // 2]) / 2
    # Act
    actual = result.median(ResultField.SIZE)
    # Assert
    assert actual == expected, f"Median size should be {expected}, got {actual}"


@pytest.mark.usefixtures("test_result_files")
def test_count(test_result_files: list[pathlib.Path]) -> None:
    """Test count aggregation for number of files."""
    # Arrange
    result = ResultSet(test_result_files)
    expected = len(test_result_files)
    # Act
    actual = result.count_()
    # Assert
    assert actual == expected, f"Count should be {expected}, got {actual}"


@pytest.mark.usefixtures("test_result_files_with_mtime")
def test_min_max_size(test_result_files_with_mtime: list[pathlib.Path]) -> None:
    """Test min and max aggregations on file size."""
    # Arrange
    rs = ResultSet(test_result_files_with_mtime)
    expected_min = 100
    expected_max = 180
    # Act
    actual_min = rs.min(ResultField.SIZE)
    actual_max = rs.max(ResultField.SIZE)
    # Assert
    assert actual_min == expected_min, (
        f"Min size should be {expected_min}, got {actual_min}"
    )
    assert actual_max == expected_max, (
        f"Max size should be {expected_max}, got {actual_max}"
    )


@pytest.mark.usefixtures("test_result_files_with_mtime")
def test_min_max_mtime(test_result_files_with_mtime: list[pathlib.Path]) -> None:
    """Test min and max aggregations on modification time."""
    # Arrange
    rs = ResultSet(test_result_files_with_mtime)
    mtimes = [f.stat().st_mtime for f in rs]
    expected_min = min(mtimes)
    expected_max = max(mtimes)
    # Act
    actual_min = rs.min(ResultField.MTIME)
    actual_max = rs.max(ResultField.MTIME)
    # Assert
    assert actual_min == expected_min, (
        f"Min mtime should match oldest file: {expected_min}, got {actual_min}"
    )
    assert actual_max == expected_max, (
        f"Max mtime should match youngest file: {expected_max}, got {actual_max}"
    )


@pytest.mark.usefixtures("test_result_folder")
def test_end_to_end_query_and_aggregations(test_result_folder: pathlib.Path) -> None:
    """End-to-end: filter files, aggregate, and verify results."""
    # Arrange
    query = Query(where_expr=Suffix("txt"))

    # Act
    expected_files: int = 15  # Should return 15 files.
    files = query.select(test_result_folder)

    # Assert
    assert expected_files == len(files), (
        f"Expected {expected_files} files, got {len(files)}"
    )

@pytest.fixture
def sample_files(tmp_path):
    """Create sample files with different names and sizes."""
    files = []
    for i, name in enumerate(["a.txt", "b.md", "c.log"]):
        f = tmp_path / name
        f.write_text("x" * (i + 1))  # size: 1, 2, 3
        files.append(f)
    return ResultSet(files)

def test_resultset_name_suffix_stem(sample_files):
    """Test extraction of name, suffix, and stem fields."""
    # Arrange
    rs = sample_files
    # Act & Assert
    names = [f.name for f in rs]
    suffixes = [f.suffix for f in rs]
    stems = [f.stem for f in rs]
    assert rs.max(ResultField.NAME) == max(names)
    assert rs.min(ResultField.NAME) == min(names)
    assert rs.max(ResultField.SUFFIX) == max(suffixes)
    assert rs.min(ResultField.SUFFIX) == min(suffixes)
    assert rs.max(ResultField.STEM) == max(stems)
    assert rs.min(ResultField.STEM) == min(stems)

def test_resultset_path_parent_parents(sample_files):
    """Test extraction of path, parent, parents, parents_stem_suffix."""
    # Arrange
    rs = sample_files
    # Act & Assert
    assert all(isinstance(rs.max(ResultField.PATH), str) for _ in rs)
    assert all(isinstance(rs.min(ResultField.PARENT), str) for _ in rs)
    assert all(isinstance(rs.max(ResultField.PARENTS), tuple) for _ in rs)
    assert all(isinstance(rs.min(ResultField.PARENTS_STEM_SUFFIX), tuple) for _ in rs)

def test_resultset_size_fields(sample_files):
    """Test extraction of size field."""
    # Arrange
    rs = sample_files
    # Act & Assert
    assert isinstance(rs.max(ResultField.SIZE), int)
    assert isinstance(rs.min(ResultField.SIZE), int)

def test_resultset_aggregates(sample_files):
    """Test average, median, count_, sort_, top_n, bottom_n."""
    # Arrange
    rs = sample_files
    # Act
    avg_size = rs.average(ResultField.SIZE)
    med_size = rs.median(ResultField.SIZE)
    count = rs.count_()
    sorted_rs = rs.sort_(ResultField.SIZE)
    top = rs.top_n(ResultField.SIZE, 2)
    bottom = rs.bottom_n(ResultField.SIZE, 2)
    # Assert
    sizes = [f.stat().st_size for f in rs]
    assert avg_size == pytest.approx(sum(sizes) / len(rs))
    assert med_size == 2
    assert count == 3
    assert sorted_rs[0].stat().st_size == 1
    assert top[0].stat().st_size == 3
    assert bottom[0].stat().st_size == 1

def test_resultset_empty():
    """Test aggregates on empty ResultSet."""
    # Arrange
    rs = ResultSet([])
    # Act & Assert
    assert rs.max(ResultField.SIZE) is None
    assert rs.min(ResultField.SIZE) is None
    assert rs.average(ResultField.SIZE) is None
    assert rs.median(ResultField.SIZE) is None
    assert rs.count_() == 0
    assert rs.top_n(ResultField.SIZE, 2) == []
    assert rs.bottom_n(ResultField.SIZE, 2) == []

def test_resultset_invalid_field(sample_files):
    """Test ValueError for unknown ResultField."""
    # Arrange
    rs = sample_files
    # Act & Assert
    with pytest.raises(ValueError):
        rs.max("not_a_field")