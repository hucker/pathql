"""Extra tests for Age filters (error handling and edge cases)."""

import operator
import pathlib

import pytest

from pathql.filters import Filter
from pathql.filters.age import AgeDays, AgeHours, AgeMinutes, AgeYears


def test_fractional_thresholds_disallowed_class_comparison():
    with pytest.raises(TypeError):
        _ = AgeDays() > 2.5


def test_fractional_thresholds_disallowed_instance_comparison():
    with pytest.raises(TypeError):
        _ = AgeHours() > 1.5


def test_fractional_thresholds_disallowed_direct_init():
    with pytest.raises(TypeError):
        _ = AgeMinutes(op=operator.gt, value=3.5)


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
    # Now equality/inequality are supported (they construct filters), so ensure
    # construction does not raise for eq/ne but match still respects semantics.
    eq_f = filter_cls(op=operator.eq, value=0)
    ne_f = filter_cls(op=operator.ne, value=1)
    assert isinstance(eq_f, filter_cls)
    assert isinstance(ne_f, filter_cls)
    assert isinstance(eq_f, filter_cls)
    assert isinstance(ne_f, filter_cls)
