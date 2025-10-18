"""
Extra tests for AgeDays, AgeYears, AgeHours, AgeMinutes filters.
Includes error handling, edge cases, and robust age comparison logic.
"""

import pytest
import pathlib
import datetime as dt
import operator
from pathql.filters.age import AgeDays, AgeYears, AgeHours, AgeMinutes
from pathql.filters import Filter

def make_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Create a temporary file for age filter tests.

    Args:
        tmp_path: Temporary directory provided by pytest.

    Returns:
        pathlib.Path: Path to the created file.
    """
    file = tmp_path / "afile.txt"
    file.write_text("x")
    return file


@pytest.mark.parametrize("filter_cls", [AgeDays, AgeYears, AgeHours, AgeMinutes])
def test_age_error(tmp_path: pathlib.Path, filter_cls:type[Filter]):
    """
    Test error handling for age filters.

    - Missing required arguments should raise TypeError.
    - Using == or != as operator should raise TypeError.
    """
    file = make_file(tmp_path)
    # Missing required arguments should raise TypeError
    with pytest.raises(TypeError):
        filter_cls().match(file)
    # Using == or != as operator should raise TypeError
    # The following lines intentionally use invalid operators; IDEs may flag these as always raising TypeError.
    # This is expected and correct for this test.
    with pytest.raises(TypeError):
        filter_cls(operator.eq, 1).match(file)  # IDE: operator.eq should always raise TypeError
    with pytest.raises(TypeError):
        filter_cls(operator.ne, 1).match(file)  # IDE: operator.ne should always raise TypeError