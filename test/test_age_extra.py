"""Extra tests for Age filters (error handling and edge cases)."""
import operator
import pathlib
import pytest

from pathql.filters.age import AgeDays, AgeYears, AgeHours, AgeMinutes
from pathql.filters import Filter

def make_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """Create a temporary file for age filter tests."""
    file = tmp_path / "a_file.txt"
    file.write_text("x")
    return file


@pytest.mark.parametrize("filter_cls", [AgeDays, AgeYears, AgeHours, AgeMinutes])
def test_age_error(
    tmp_path: pathlib.Path,
    filter_cls: type[Filter],
) -> None:
    """Age filters raise TypeError for missing args or unsupported operators."""
    # Arrange
    file = make_file(tmp_path)

    # Act and Assert
    # Missing required arguments should raise TypeError
    with pytest.raises(TypeError):
        filter_cls().match(file)

    # Unsupported operators should raise TypeError at construction
    with pytest.raises(TypeError):
        filter_cls(operator.eq, 1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        filter_cls(operator.ne, 1)  # type: ignore[arg-type]
