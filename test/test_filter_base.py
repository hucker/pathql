"""
Unit tests for logical filter combinators in pathql.filters.base.

Covers AndFilter, OrFilter, NotFilter, AllowAll, and AllowNone.
Each test uses the Arrange-Act-Assert (AAA) pattern for clarity.
"""

import pathlib
import pytest
from pathql.filters.base import Filter, AndFilter, OrFilter, NotFilter, AllowAll, AllowNone

class AlwaysTrue(Filter):
    """Dummy filter that always matches."""
    def match(self, path, stat_proxy=None, now=None):
        return True

class AlwaysFalse(Filter):
    """Dummy filter that never matches."""
    def match(self, path, stat_proxy=None, now=None):
        return False

def test_and_filter_match_true_true():
    """AndFilter: both True."""
    # Arrange
    f1 = AlwaysTrue()
    f2 = AlwaysTrue()
    and_filter = AndFilter(f1, f2)
    # Act
    result = and_filter.match(pathlib.Path("foo"))
    # Assert
    assert result

def test_and_filter_match_true_false():
    """AndFilter: True and False."""
    # Arrange
    f1 = AlwaysTrue()
    f2 = AlwaysFalse()
    and_filter = AndFilter(f1, f2)
    # Act
    result = and_filter.match(pathlib.Path("foo"))
    # Assert
    assert not result

def test_and_filter_match_false_true():
    """AndFilter: False and True."""
    # Arrange
    f1 = AlwaysFalse()
    f2 = AlwaysTrue()
    and_filter = AndFilter(f1, f2)
    # Act
    result = and_filter.match(pathlib.Path("foo"))
    # Assert
    assert not result

def test_and_filter_match_false_false():
    """AndFilter: both False."""
    # Arrange
    f1 = AlwaysFalse()
    f2 = AlwaysFalse()
    and_filter = AndFilter(f1, f2)
    # Act
    result = and_filter.match(pathlib.Path("foo"))
    # Assert
    assert not result

def test_and_operator_chaining():
    """AndFilter: chaining with & operator."""
    # Arrange
    f1 = AlwaysTrue()
    f2 = AlwaysTrue()
    f3 = AlwaysFalse()
    # Act
    chained = f1 & f2 & f3
    result = chained.match(pathlib.Path("foo"))
    # Assert
    assert not result

def test_or_filter_match_true_true():
    """OrFilter: both True."""
    # Arrange
    f1 = AlwaysTrue()
    f2 = AlwaysTrue()
    or_filter = OrFilter(f1, f2)
    # Act
    result = or_filter.match(pathlib.Path("foo"))
    # Assert
    assert result

def test_or_filter_match_true_false():
    """OrFilter: True or False."""
    # Arrange
    f1 = AlwaysTrue()
    f2 = AlwaysFalse()
    or_filter = OrFilter(f1, f2)
    # Act
    result = or_filter.match(pathlib.Path("foo"))
    # Assert
    assert result

def test_or_filter_match_false_true():
    """OrFilter: False or True."""
    # Arrange
    f1 = AlwaysFalse()
    f2 = AlwaysTrue()
    or_filter = OrFilter(f1, f2)
    # Act
    result = or_filter.match(pathlib.Path("foo"))
    # Assert
    assert result

def test_or_filter_match_false_false():
    """OrFilter: both False."""
    # Arrange
    f1 = AlwaysFalse()
    f2 = AlwaysFalse()
    or_filter = OrFilter(f1, f2)
    # Act
    result = or_filter.match(pathlib.Path("foo"))
    # Assert
    assert not result

def test_or_operator_chaining():
    """OrFilter: chaining with | operator."""
    # Arrange
    f1 = AlwaysFalse()
    f2 = AlwaysFalse()
    f3 = AlwaysTrue()
    # Act
    chained = f1 | f2 | f3
    result = chained.match(pathlib.Path("foo"))
    # Assert
    assert result

def test_not_filter_true():
    """NotFilter: negates True."""
    # Arrange
    f = AlwaysTrue()
    not_filter = NotFilter(f)
    # Act
    result = not_filter.match(pathlib.Path("foo"))
    # Assert
    assert not result

def test_not_filter_false():
    """NotFilter: negates False."""
    # Arrange
    f = AlwaysFalse()
    not_filter = NotFilter(f)
    # Act
    result = not_filter.match(pathlib.Path("foo"))
    # Assert
    assert result

def test_not_operator():
    """NotFilter: ~ operator."""
    # Arrange
    f = AlwaysTrue()
    f2 = AlwaysFalse()
    # Act
    not_filter = ~f
    not_filter2 = ~f2
    # Assert
    assert not not_filter.match(pathlib.Path("foo"))
    assert not_filter2.match(pathlib.Path("foo"))

def test_allowall_and_allownone():
    """AllowAll and AllowNone filters."""
    # Arrange
    allow_all = AllowAll()
    allow_none = AllowNone()
    # Act
    result_all = allow_all.match(pathlib.Path("foo"))
    result_none = allow_none.match(pathlib.Path("foo"))
    # Assert
    assert result_all
    assert not result_none