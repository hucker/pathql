"""
Tests for StatProxy call counts in PathQL filters.

This module verifies that stat-based filters and their combinators
call StatProxy.stat() the expected number of times, including cases
where short-circuiting in OR combinators reduces the number of stat calls.
"""
import pathlib
import pytest

from pathql.filters.base import Filter
from pathql.filters.age import AgeDays
from pathql.filters.size import Size
from pathql.filters.suffix import Suffix
from pathql.filters.stat_proxy import StatProxy
from pathql.query import Query


@pytest.mark.parametrize(
    "filter_expr,expected_calls",
    [
        # Single stat-based filter: always one stat call
        (Suffix("txt"), 0),  # Suffix filter should call stat 0 times since it doesn't need stat
        
        (Size() > 10, 1),  # Size filter should call stat once
        (AgeDays() < 5, 1),  # Age filter should call stat once
        # AND combinator: both filters are always evaluated, so two stat calls
        ((Size() > 10) & (AgeDays() < 5), 2),  # AND: two stat calls
        # OR combinator: short-circuiting means only one stat call if the first filter matches
        (
            (Size() > 10) | (AgeDays() < 5),
            1,
        ),  # OR: only one stat call due to short-circuiting
        # In this test, Size() > 10 matches, so AgeDays() < 5 is not evaluated
        # Nested combinators: AND always evaluates both sides, OR may short-circuit
        ((Size() > 10) & ((AgeDays() < 5) | (Size() < 100)), 2),  # AND: two stat calls
        # Here, the left side (Size() > 10) matches, and the right side is an OR where the first filter (AgeDays() < 5) does not match,
        # so the second filter (Size() < 100) is evaluated, but overall only two stat calls are made
        (Size() > 10, 1),  # Repeat for coverage
    ],
)
def test_stat_proxy_call_count(tmp_path:pathlib.Path, filter_expr:Filter, expected_calls:int) -> None:
    """
    Test that StatProxy.stat_calls matches the expected count for each filter expression.

    - Single stat-based filters should call stat once.
    - AND combinators always evaluate both sides, so two stat calls.
    - OR combinators may short-circuit: if the first filter matches, the second is not evaluated, so only one stat call.
    - Nested combinators follow the same rules recursively.
    """
    # Arrange: create a file and StatProxy
    file:pathlib.Path = tmp_path / "testfile.txt"
    file.write_bytes(b"x" * 50)
    proxy = StatProxy(file)
    query = Query(filter_expr)

    # Act: run the query
    query.match(file, proxy)

    # Assert: check stat call count with detailed message
    assert proxy.stat_calls == expected_calls, (
        f"StatProxy call count mismatch: expected {expected_calls} for filter '{filter_expr}', "
        f"but got {proxy.stat_calls}. "
        f"Reason: "
        f"Single filters always call stat once. "
        f"AND combinators always evaluate both sides (two stat calls). "
        f"OR combinators may short-circuit, reducing stat calls if the first filter matches. "
        f"Nested combinators follow these rules recursively."
    )

