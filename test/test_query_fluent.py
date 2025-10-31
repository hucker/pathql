"""
Tests for the fluent Query API in pathql.

This module verifies that Query supports both classic and builder-style configuration,
correctly filters files, and that builder methods configure state identically to the constructor.
All tests use the Arrange-Act-Assert (AAA) pattern for clarity.
"""

import datetime as dt

from pathql.filters.suffix import Suffix
from pathql.query import Query


def test_internal_state_equivalence():
    """Internal state is the same between __init__ setup and fluent setup."""
    # Arrange
    from_paths = "/tmp"
    where_expr = Suffix() == "txt"
    recursive = False
    files_only = False
    now = dt.datetime(2025, 1, 1, 12, 0, 0)
    threaded = True

    # Act
    q_ctor = Query(
        from_paths=from_paths,
        where_expr=where_expr,
        recursive=recursive,
        files_only=files_only,
        now=now,
        threaded=threaded,
    )
    q_fluent = (
        Query()
        .from_paths(from_paths)
        .where(where_expr)
        .recursive(recursive)
        .files_only(files_only)
        .at_time(now)
        .threaded(threaded)
    )

    # Assert
    assert q_ctor.get_from_paths == q_fluent.get_from_paths
    assert q_ctor.get_where_expr == q_fluent.get_where_expr
    assert q_ctor.get_recursive == q_fluent.get_recursive
    assert q_ctor.get_files_only == q_fluent.get_files_only
    assert q_ctor.get_now == q_fluent.get_now
    assert q_ctor.get_threaded == q_fluent.get_threaded


def test_fluent_reverse_order_equivalence():
    """Internal state is the same when fluent parameters are set in reverse order."""
    # Arrange
    from_paths = "/tmp"
    where_expr = Suffix() == "txt"
    recursive = False
    files_only = False
    now = dt.datetime(2025, 1, 1, 12, 0, 0)
    threaded = True

    # Act
    q_normal = (
        Query()
        .from_paths(from_paths)
        .where(where_expr)
        .recursive(recursive)
        .files_only(files_only)
        .at_time(now)
        .threaded(threaded)
    )
    q_reverse = (
        Query()
        .threaded(threaded)
        .at_time(now)
        .files_only(files_only)
        .recursive(recursive)
        .where(where_expr)
        .from_paths(from_paths)
    )

    # Assert
    assert q_normal.get_from_paths == q_reverse.get_from_paths
    assert q_normal.get_where_expr == q_reverse.get_where_expr
    assert q_normal.get_recursive == q_reverse.get_recursive
    assert q_normal.get_files_only == q_reverse.get_files_only
    assert q_normal.get_now == q_reverse.get_now
    assert q_normal.get_threaded == q_reverse.get_threaded
