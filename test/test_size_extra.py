"""Extra tests for Size filter, including error handling and custom file creation."""
import pathlib
import pytest
from pathql.filters.size import Size

def make_file(tmp_path: pathlib.Path, size: int = 1) -> pathlib.Path:
    """Helper function to create a file of a specific size."""
    file = tmp_path / "afile.txt"
    file.write_bytes(b"x" * size)
    return file

def test_size_basic(tmp_path: pathlib.Path) -> None:
    """Test basic size filter functionality.

    - Arrange: Create a file of a specific size.
    - Act: Apply size filters.
    - Assert: Verify the filters match as expected.
    """
    # Arrange
    file = make_file(tmp_path, 100)

    # Act and Assert
    assert Size(lambda x, y: x == y, 100).match(file)
    assert Size(lambda x, y: x < y, 200).match(file)
    assert not Size(lambda x, y: x > y, 200).match(file)

def test_size_error() -> None:
    """Test error handling in size filter.

    - Arrange: Create a mock object that raises an error on stat.
    - Act: Apply size filter to the mock object.
    - Assert: Verify the filter handles errors gracefully.
    """
    # Act and Assert
    assert Size(lambda x, y: x < y, 1).match(pathlib.Path("afile.txt")) is False
    with pytest.raises(TypeError):
        Size().match(pathlib.Path("afile.txt"))

def test_size_operator_overloads(tmp_path: pathlib.Path) -> None:
    """Test operator overloads for size filter.

    - Arrange: Create a file of a specific size.
    - Act: Apply various operator overloads.
    - Assert: Verify the operators behave as expected.
    """
    # Arrange
    file = make_file(tmp_path, 50)

    # Act and Assert
    assert Size() <= 100
    assert Size() < 1000
    assert Size() >= 10
    assert Size() > 1
    assert Size() == 50
    assert Size() != 51
    assert Size(lambda x, y: x == y, 50).match(file)
