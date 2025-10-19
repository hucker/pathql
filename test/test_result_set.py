"""
Tests for ResultSet aggregations in PathQL.

Covers max, min, top_n, bottom_n, sort, average, median, and count operations on a known set of files.
"""

import pytest
from pathlib import Path
from pathql.result_set import ResultSet, ResultField
from pathql.query import Query
from pathql.filters.suffix import Suffix

@pytest.mark.usefixtures("test_result_files")
def test_max_size(test_result_files: list[Path]) -> None:
    """
    Test max aggregation by file size.

    - Arrange: Create a ResultSet from test files.
    - Act: Compute the maximum file size.
    - Assert: Verify the maximum size matches the expected value.
    """
    # Arrange
    result = ResultSet(test_result_files)

    # Act
    max_size = result.max(ResultField.SIZE)

    # Assert
    assert max_size == 3000, "Max size should be 3000 (largest_1.txt)"

@pytest.mark.usefixtures("test_result_files")
def test_min_size(test_result_files: list[Path]) -> None:
    """
    Test min aggregation by file size.

    - Arrange: Create a ResultSet from test files.
    - Act: Compute the minimum file size.
    - Assert: Verify the minimum size matches the expected value.
    """
    # Arrange
    result = ResultSet(test_result_files)

    # Act
    min_size = result.min(ResultField.SIZE)

    # Assert
    assert min_size == 10, "Min size should be 10 (smallest_1.txt)"

@pytest.mark.usefixtures("test_result_files")
def test_top3_largest(test_result_files: list[Path]) -> None:
    """
    Test top_n aggregation for largest files by size.

    - Arrange: Create a ResultSet from test files.
    - Act: Retrieve the top 3 largest files by size.
    - Assert: Verify the top 3 files match the expected values.
    """
    # Arrange
    result = ResultSet(test_result_files)

    # Act
    top3 = result.top_n(ResultField.SIZE, 3)
    names = {p.name for p in top3}

    # Assert
    expected_names = {"largest_1.txt", "largest_2.txt", "largest_3.txt"}
    assert names == expected_names, f"Top 3 largest files should be {expected_names}, got {names}"

@pytest.mark.usefixtures("test_result_files")
def test_bottom3_smallest(test_result_files: list[Path]) -> None:
    """
    Test bottom_n aggregation for smallest files by size.

    - Arrange: Create a ResultSet from test files.
    - Act: Retrieve the bottom 3 smallest files by size.
    - Assert: Verify the bottom 3 files match the expected values.
    """
    # Arrange
    result = ResultSet(test_result_files)

    # Act
    bottom3 = result.bottom_n(ResultField.SIZE, 3)
    names = {p.name for p in bottom3}

    # Assert
    expected_names = {"smallest_1.txt", "smallest_2.txt", "smallest_3.txt"}
    assert names == expected_names, f"Bottom 3 smallest files should be {expected_names}, got {names}"

@pytest.mark.usefixtures("test_result_files")
def test_sort_by_name(test_result_files: list[Path]) -> None:
    """
    Test sorting files by name.

    - Arrange: Create a ResultSet from test files.
    - Act: Sort the files by name.
    - Assert: Verify the first and last file names match the expected values.
    """
    # Arrange
    result = ResultSet(test_result_files)

    # Act
    sorted_names = [p.name for p in result.sort_(ResultField.NAME)]

    # Assert
    assert sorted_names[0] == "a_first.txt", f"First file by name should be 'a_first.txt', got {sorted_names[0]}"
    assert sorted_names[-1] == "z_last.txt", f"Last file by name should be 'z_last.txt', got {sorted_names[-1]}"

@pytest.mark.usefixtures("test_result_files")
def test_average_size(test_result_files: list[Path]) -> None:
    """
    Test average aggregation by file size.

    - Arrange: Create a ResultSet from test files.
    - Act: Compute the average file size.
    - Assert: Verify the average size matches the expected value.
    """
    # Arrange
    result = ResultSet(test_result_files)
    expected_avg = sum(p.stat().st_size for p in result) / len(result)

    # Act
    actual_avg = result.average(ResultField.SIZE)

    # Assert
    assert actual_avg == expected_avg, f"Average size should be {expected_avg}, got {actual_avg}"

@pytest.mark.usefixtures("test_result_files")
def test_median_size(test_result_files: list[Path]) -> None:
    """
    Test median aggregation by file size.

    - Arrange: Create a ResultSet from test files.
    - Act: Compute the median file size.
    - Assert: Verify the median size matches the expected value.
    """
    # Arrange
    result = ResultSet(test_result_files)
    sizes = sorted(p.stat().st_size for p in result)
    n = len(sizes)
    mid = n // 2
    expected_median = sizes[mid] if n % 2 else (sizes[mid - 1] + sizes[mid]) / 2

    # Act
    actual_median = result.median(ResultField.SIZE)

    # Assert
    assert actual_median == expected_median, f"Median size should be {expected_median}, got {actual_median}"

@pytest.mark.usefixtures("test_result_files")
def test_count(test_result_files: list[Path]) -> None:
    """
    Test count aggregation for number of files.

    - Arrange: Create a ResultSet from test files.
    - Act: Count the number of files.
    - Assert: Verify the count matches the expected value.
    """
    # Arrange
    result = ResultSet(test_result_files)
    expected_count = len(test_result_files)

    # Act
    actual_count = result.count_()

    # Assert
    assert actual_count == expected_count, f"Count should be {expected_count}, got {actual_count}"

@pytest.mark.usefixtures("test_result_files_with_mtime")
def test_min_max_size(test_result_files_with_mtime: list[Path]) -> None:
    """
    Test min and max aggregations on file size.

    - Arrange: Create a ResultSet from test files with modification times.
    - Act: Compute the minimum and maximum file sizes.
    - Assert: Verify the min and max sizes match the expected values.
    """
    # Arrange
    rs = ResultSet(test_result_files_with_mtime)

    # Act and Assert
    assert rs.min(ResultField.SIZE) == 100, "Min size should be 100"
    assert rs.max(ResultField.SIZE) == 180, "Max size should be 180"

@pytest.mark.usefixtures("test_result_files_with_mtime")
def test_min_max_mtime(test_result_files_with_mtime: list[Path]) -> None:
    """
    Test min and max aggregations on modification time (age).

    - Arrange: Create a ResultSet from test files with modification times.
    - Act: Compute the minimum and maximum modification times.
    - Assert: Verify the min and max modification times match the expected values.
    """
    # Arrange
    rs = ResultSet(test_result_files_with_mtime)
    mtimes = [f.stat().st_mtime for f in rs]

    # Act and Assert
    assert rs.min(ResultField.MTIME) == min(mtimes), "Min mtime should match oldest file"
    assert rs.max(ResultField.MTIME) == max(mtimes), "Max mtime should match youngest file"

@pytest.mark.usefixtures("test_result_folder")
def test_end_to_end_query_and_aggregations(test_result_folder: Path) -> None:
    """
    End-to-end test: filter files, aggregate, and sort.

    - Arrange: Set up a test folder and a Query for files with suffix '.txt'.
    - Act: Execute the query and perform aggregations.
    - Assert: Verify the results meet the expected criteria.
    """
    # Arrange
    query = Query(Suffix == "txt")

    # Act
    expected_files:int = 15. # Should return 15 files.
    files = query.select(test_result_folder)

    # Assert
    assert expected_files == len(files), f"Expected {expected_files} files, got {len(files)}"

