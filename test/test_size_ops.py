"""Operator-based tests for Size filter, covering ==, !=, <, >, <=, >= cases."""

from conftest_size import size_test_folder
import pathlib
from pathql.filters.size import Size

def test_size_eq(size_test_folder):
    # Should match files with exact size using == operator
    files = list(size_test_folder.iterdir())
    assert any((Size == 100).match(f) for f in files)
    assert any((Size == 200).match(f) for f in files)
    assert not any((Size == 150).match(f) for f in files)

def test_size_ne(size_test_folder):
    # Should match files not equal to a given size using != operator
    files = list(size_test_folder.iterdir())
    assert all((Size != 150).match(f) for f in files)
    assert any((Size != 100).match(f) for f in files)

def test_size_lt(size_test_folder):
    # Should match files less than a given size using < operator
    files = list(size_test_folder.iterdir())
    assert all((Size < 300).match(f) for f in files)
    assert any((Size < 150).match(f) for f in files)
    assert not any((Size < 100).match(f) for f in files)

def test_size_le(size_test_folder):
    # Should match files less than or equal to a given size using <= operator
    files = list(size_test_folder.iterdir())
    assert all((Size <= 200).match(f) for f in files)
    assert any((Size <= 100).match(f) for f in files)
    assert not any((Size <= 50).match(f) for f in files)

def test_size_gt(size_test_folder):
    # Should match files greater than a given size using > operator
    files = list(size_test_folder.iterdir())
    assert any((Size > 100).match(f) for f in files)
    assert not any((Size > 200).match(f) for f in files)

def test_size_ge(size_test_folder):
    # Should match files greater than or equal to a given size using >= operator
    files = list(size_test_folder.iterdir())
    assert all((Size >= 100).match(f) for f in files)
    assert any((Size >= 200).match(f) for f in files)
    assert not any((Size >= 300).match(f) for f in files)
