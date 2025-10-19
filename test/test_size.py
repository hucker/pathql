"""
Tests for Size filter using a fixture with files of known sizes.
"""

# Tests for Size filter using the size_test_folder fixture.
# size_test_folder contains:
#   100.txt (100 bytes)
#   200.txt (200 bytes)

import pathlib
from pathql.filters.size import Size

def test_size_eq(size_test_folder: pathlib.Path) -> None:
    """
    Test Size == operator.

    - Arrange: Retrieve test files.
    - Act: Apply equality filter.
    - Assert: Verify matching files.
    """
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert any((Size() == 100).match(f) for f in files)
    assert any((Size() == 200).match(f) for f in files)
    assert not any((Size() == 150).match(f) for f in files)

def test_size_ne(size_test_folder: pathlib.Path) -> None:
    """
    Test Size != operator.

    - Arrange: Retrieve test files.
    - Act: Apply inequality filter.
    - Assert: Verify matching files.
    """
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() != 150).match(f) for f in files)
    assert any((Size() != 100).match(f) for f in files)

def test_size_lt(size_test_folder: pathlib.Path) -> None:
    """
    Test Size < operator.

    - Arrange: Retrieve test files.
    - Act: Apply less-than filter.
    - Assert: Verify matching files.
    """
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() < 300).match(f) for f in files)
    assert any((Size() < 150).match(f) for f in files)
    assert not any((Size() < 100).match(f) for f in files)

def test_size_le(size_test_folder: pathlib.Path) -> None:
    """
    Test Size <= operator.

    - Arrange: Retrieve test files.
    - Act: Apply less-than-or-equal filter.
    - Assert: Verify matching files.
    """
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() <= 200).match(f) for f in files)
    assert any((Size() <= 100).match(f) for f in files)
    assert not any((Size() <= 50).match(f) for f in files)

def test_size_gt(size_test_folder: pathlib.Path) -> None:
    """
    Test Size > operator.

    - Arrange: Retrieve test files.
    - Act: Apply greater-than filter.
    - Assert: Verify matching files.
    """
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert any((Size() > 100).match(f) for f in files)
    assert not any((Size() > 200).match(f) for f in files)

def test_size_ge(size_test_folder: pathlib.Path) -> None:
    """
    Test Size >= operator.

    - Arrange: Retrieve test files.
    - Act: Apply greater-than-or-equal filter.
    - Assert: Verify matching files.
    """
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act and Assert
    assert all((Size() >= 100).match(f) for f in files)
    assert any((Size() >= 200).match(f) for f in files)
    assert not any((Size() >= 300).match(f) for f in files)
