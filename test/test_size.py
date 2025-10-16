"""Tests for Size filter using a fixture with files of known sizes."""


# Tests for Size filter using the size_test_folder fixture.
# size_test_folder contains:
#   100.txt (100 bytes)
#   200.txt (200 bytes)

import pathlib
from pathql.filters.size import Size

def test_size_eq(size_test_folder):
    """Test Size == operator."""
    files = list(size_test_folder.iterdir())
    assert any((Size == 100).match(f) for f in files)
    assert any((Size == 200).match(f) for f in files)
    assert not any((Size == 150).match(f) for f in files)

def test_size_ne(size_test_folder):
    """Test Size != operator."""
    files = list(size_test_folder.iterdir())
    assert all((Size != 150).match(f) for f in files)
    assert any((Size != 100).match(f) for f in files)

def test_size_lt(size_test_folder):
    """Test Size < operator."""
    files = list(size_test_folder.iterdir())
    assert all((Size < 300).match(f) for f in files)
    assert any((Size < 150).match(f) for f in files)
    assert not any((Size < 100).match(f) for f in files)

def test_size_le(size_test_folder):
    """Test Size <= operator."""
    files = list(size_test_folder.iterdir())
    assert all((Size <= 200).match(f) for f in files)
    assert any((Size <= 100).match(f) for f in files)
    assert not any((Size <= 50).match(f) for f in files)

def test_size_gt(size_test_folder):
    """Test Size > operator."""
    files = list(size_test_folder.iterdir())
    assert any((Size > 100).match(f) for f in files)
    assert not any((Size > 200).match(f) for f in files)

def test_size_ge(size_test_folder):
    """Test Size >= operator."""
    files = list(size_test_folder.iterdir())
    assert all((Size >= 100).match(f) for f in files)
    assert any((Size >= 200).match(f) for f in files)
    assert not any((Size >= 300).match(f) for f in files)
