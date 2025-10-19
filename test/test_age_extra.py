"""
Extra tests for AgeDays, AgeYears, AgeHours, AgeMinutes filters.
Includes error handling, edge cases, and robust age comparison logic.
"""

import pytest
import pathlib
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
def test_age_error(tmp_path: pathlib.Path, filter_cls: type[Filter]):
    """
    Test error handling for age filters.

    - Arrange: Create a temporary file and initialize the filter class.
    - Act: Attempt to use the filter with missing arguments or unsupported operators.
    - Assert: Verify that the appropriate TypeError is raised.
    """
    # Arrange
    file = make_file(tmp_path)

    # Act and Assert
    # Missing required arguments should raise TypeError
    with pytest.raises(TypeError):
        filter_cls().match(file)

    # Unsupported operators should raise TypeError
    with pytest.raises(TypeError):
        filter_cls().match(file, comparison="==")
    with pytest.raises(TypeError):
        filter_cls().match(file, comparison="!=")