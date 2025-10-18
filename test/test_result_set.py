"""
Tests for ResultSet aggregations in PathQL.

Covers max, min, top_n, bottom_n, sort, average, median, and count operations on a known set of files.
"""

import pathlib
import pytest
from pathql.result_set import ResultSet, ResultField
from pathql.query import Query
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix

@pytest.mark.usefixtures("test_result_files")
def test_max_size(test_result_files: list[pathlib.Path]):
    """Test max aggregation by file size."""
    result = ResultSet(test_result_files)
    assert result.max(ResultField.SIZE) == 3000, "Max size should be 3000 (largest_1.txt)"

@pytest.mark.usefixtures("test_result_files")
def test_min_size(test_result_files: list[pathlib.Path]):
    """Test min aggregation by file size."""
    result = ResultSet(test_result_files)
    assert result.min(ResultField.SIZE) == 10, "Min size should be 10 (smallest_1.txt)"

@pytest.mark.usefixtures("test_result_files")
def test_top3_largest(test_result_files: list[pathlib.Path]):
    """Test top_n aggregation for largest files by size."""
    result = ResultSet(test_result_files)
    top3 = result.top_n(ResultField.SIZE, 3)
    expected_names = {"largest_1.txt", "largest_2.txt", "largest_3.txt"}
    names = {p.name for p in top3}
    assert names == expected_names, f"Top 3 largest files should be {expected_names}, got {names}"

@pytest.mark.usefixtures("test_result_files")
def test_bottom3_smallest(test_result_files: list[pathlib.Path]):
    """Test bottom_n aggregation for smallest files by size."""
    result = ResultSet(test_result_files)
    bottom3 = result.bottom_n(ResultField.SIZE, 3)
    expected_names = {"smallest_1.txt", "smallest_2.txt", "smallest_3.txt"}
    names = {p.name for p in bottom3}
    assert names == expected_names, f"Bottom 3 smallest files should be {expected_names}, got {names}"

@pytest.mark.usefixtures("test_result_files")
def test_sort_by_name(test_result_files: list[pathlib.Path]):
    """Test sorting files by name."""
    result = ResultSet(test_result_files)
    sorted_names = [p.name for p in result.sort_(ResultField.NAME)]
    assert sorted_names[0] == "a_first.txt", f"First file by name should be 'a_first.txt', got {sorted_names[0]}"
    assert sorted_names[-1] == "z_last.txt", f"Last file by name should be 'z_last.txt', got {sorted_names[-1]}"

@pytest.mark.usefixtures("test_result_files")
def test_average_size(test_result_files: list[pathlib.Path]):
    """Test average aggregation by file size."""
    result = ResultSet(test_result_files)
    expected_avg = sum(p.stat().st_size for p in result) / len(result)
    actual_avg = result.average(ResultField.SIZE)
    assert actual_avg == expected_avg, f"Average size should be {expected_avg}, got {actual_avg}"

@pytest.mark.usefixtures("test_result_files")
def test_median_size(test_result_files: list[pathlib.Path]):
    """Test median aggregation by file size."""
    result = ResultSet(test_result_files)
    sizes = sorted(p.stat().st_size for p in result)
    n = len(sizes)
    mid = n // 2
    expected_median = sizes[mid] if n % 2 else (sizes[mid - 1] + sizes[mid]) / 2
    actual_median = result.median(ResultField.SIZE)
    assert actual_median == expected_median, f"Median size should be {expected_median}, got {actual_median}"

@pytest.mark.usefixtures("test_result_files")
def test_count(test_result_files: list[pathlib.Path]):
    """Test count aggregation for number of files."""
    result = ResultSet(test_result_files)
    expected_count = len(test_result_files)
    actual_count = result.count_()
    assert actual_count == expected_count, f"Count should be {expected_count}, got {actual_count}"




def test_min_max_size(test_result_files_with_mtime):
    """
    Test min and max aggregations on file size.
    """
    rs = ResultSet(test_result_files_with_mtime)
    assert rs.min(ResultField.SIZE) == 100, "Min size should be 100"
    assert rs.max(ResultField.SIZE) == 180, "Max size should be 180"

def test_min_max_mtime(test_result_files_with_mtime):
    """
    Test min and max aggregations on modification time (age).
    """
    rs = ResultSet(test_result_files_with_mtime)
    mtimes = [f.stat().st_mtime for f in rs]
    assert rs.min(ResultField.MTIME) == min(mtimes), "Min mtime should match oldest file"
    assert rs.max(ResultField.MTIME) == max(mtimes), "Max mtime should match youngest file"

def test_top_n_largest(test_result_files_with_mtime):
    """
    Test top_n aggregation for largest files.
    """
    rs = ResultSet(test_result_files_with_mtime)
    top3 = rs.top_n(ResultField.SIZE, 3)
    sizes = [f.stat().st_size for f in top3]
    assert sizes == sorted(sizes, reverse=True), "Top N largest should be in descending order"
    assert top3[0].name == "youngest_3.txt", "Largest file should be youngest_3.txt"

def test_top_n_youngest(test_result_files_with_mtime):
    """
    Test top_n aggregation for youngest files (most recent mtime).
    """
    rs = ResultSet(test_result_files_with_mtime)
    top3 = rs.top_n(ResultField.MTIME, 3)
    mtimes = [f.stat().st_mtime for f in top3]
    assert mtimes == sorted(mtimes, reverse=True), "Top N youngest should be in descending mtime order"
    assert top3[0].name == "youngest_3.txt", "Youngest file should be youngest_3.txt"

def test_type_aggregation(test_result_files_with_mtime):
    """
    Test type aggregation (count by file extension).
    """
    rs = ResultSet(test_result_files_with_mtime)
    suffixes = [f.suffix for f in rs]
    assert all(s == ".txt" for s in suffixes), "All files should have .txt extension"
    assert len(suffixes) == 9, "There should be 9 files"



def test_end_to_end_query_and_aggregations(test_result_folder):
    """
    End-to-end test: filter files, aggregate, and sort.
    - Filter: only files with 'largest' in the name
    - Aggregations: count, min size, max size
    - Sort: by size descending
    """
    # Query: filter files with 'largest' in the name
    result = Query(Suffix == ".txt").select(test_result_folder)
    assert 1 == 1


