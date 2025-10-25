"""
Tests for short-circuiting behavior in AndFilter and OrFilter.

These tests verify that the right-hand filter is only evaluated if necessary,
using a DelayFilter that sleeps for DELAY seconds and sets a flag when called.
This ensures that boolean logic in filter composition is efficient and avoids
unnecessary computation, especially for expensive filters.
"""

import pathlib
import time

from pathql.filters.base import AndFilter, Filter, OrFilter

DELAY = 0.1  # seconds to sleep in DelayFilter
SHORT_CIRCUIT_THRESHOLD = 0.5 * DELAY  # max time for short-circuiting tests

class DelayFilter(Filter):
    """Filter that sleeps for DELAY seconds and returns a fixed boolean."""
    def __init__(self, result: bool):
        self.result = result
        self.called = False

    def match(
        self,
        path: pathlib.Path,
        stat_proxy=None,
        now=None,
    ) -> bool:
        self.called = True
        time.sleep(DELAY)
        return self.result

class TrueFilter(Filter):
    """Filter that always returns True."""
    def match(
        self,
        path: pathlib.Path,
        stat_proxy=None,
        now=None,
    ) -> bool:
        return True

class FalseFilter(Filter):
    """Filter that always returns False."""
    def match(
        self,
        path: pathlib.Path,
        stat_proxy=None,
        now=None,
    ) -> bool:
        return False

def test_and_filter_short_circuit() -> None:
    """
    Test that AndFilter short-circuits and does not call right filter if left is False.
    """
    # Arrange

    left = FalseFilter()
    right = DelayFilter(True)

    # Act

    start = time.time()
    actual_result = AndFilter(left, right).match(pathlib.Path("dummy"))
    actual_elapsed = time.time() - start

    # Assert

    assert actual_result is False
    assert not right.called  # right filter should not be called
    assert actual_elapsed < SHORT_CIRCUIT_THRESHOLD  # should be fast, no delay

def test_or_filter_short_circuit() -> None:
    """
    Test that OrFilter short-circuits and does not call right filter if left is True.
    """
    # Arrange

    left = TrueFilter()
    right = DelayFilter(True)

    # Act

    start = time.time()
    actual_result = OrFilter(left, right).match(pathlib.Path("dummy"))
    actual_elapsed = time.time() - start

    # Assert

    assert actual_result is True
    assert not right.called  # right filter should not be called
    assert actual_elapsed < SHORT_CIRCUIT_THRESHOLD  # should be fast, no delay

def test_and_filter_no_short_circuit() -> None:
    """
    Test that AndFilter does not short-circuit if left is True.
    """
    # Arrange

    left = TrueFilter()
    right = DelayFilter(True)

    # Act

    start = time.time()
    actual_result = AndFilter(left, right).match(pathlib.Path("dummy"))
    actual_elapsed = time.time() - start

    # Assert

    assert actual_result is True
    assert right.called  # right filter should be called
    assert actual_elapsed >= DELAY  # should take at least DELAY seconds

def test_or_filter_no_short_circuit() -> None:
    """
    Test that OrFilter does not short-circuit if left is False.
    """
    # Arrange

    left = FalseFilter()
    right = DelayFilter(True)

    # Act

    start = time.time()
    actual_result = OrFilter(left, right).match(pathlib.Path("dummy"))
    actual_elapsed = time.time() - start

    # Assert

    assert actual_result is True
    assert right.called  # right filter should be called
    assert actual_elapsed >= DELAY  # should take at least DELAY seconds

def test_and_filter_chain_short_circuit() -> None:
    """
    Test that chaining multiple AndFilters short-circuits after the first failure.
    Only the first filter should be executed, regardless of where the DelayFilter is placed.
    """
    # Arrange

    class FlagFilter(Filter):
        """Filter that always returns False and sets a flag when called."""
        def __init__(self):
            self.called = False
        def match(
            self,
            path: pathlib.Path,
            stat_proxy=None,
            now=None,
        ) -> bool:
            self.called = True
            return False

    # DelayFilter as A
    a = DelayFilter(False)
    b = TrueFilter()
    c = TrueFilter()
    start = time.time()
    actual_result = AndFilter(a, AndFilter(b, c)).match(pathlib.Path("dummy"))
    actual_elapsed = time.time() - start
    assert actual_result is False
    assert a.called
    assert not getattr(b, "called", False)
    assert not getattr(c, "called", False)
    assert actual_elapsed >= DELAY and actual_elapsed < DELAY * 2

    # DelayFilter as B
    a = FlagFilter()
    b = DelayFilter(False)
    c = TrueFilter()
    start = time.time()
    actual_result = AndFilter(a, AndFilter(b, c)).match(pathlib.Path("dummy"))
    actual_elapsed = time.time() - start
    assert actual_result is False
    assert a.called
    assert not b.called  # b should NOT be called because a fails
    assert not getattr(c, "called", False)
    assert actual_elapsed < SHORT_CIRCUIT_THRESHOLD

    # DelayFilter as C
    a = FlagFilter()
    b = TrueFilter()
    c = DelayFilter(False)
    start = time.time()
    actual_result = AndFilter(a, AndFilter(b, c)).match(pathlib.Path("dummy"))
    actual_elapsed = time.time() - start
    assert actual_result is False
    assert a.called
    assert not getattr(b, "called", False)
    assert not c.called  # c should NOT be called because a fails
    assert actual_elapsed < SHORT_CIRCUIT_THRESHOLD
    