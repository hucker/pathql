"""Tests for Stem filters (equality, multiple, wildcard, case, and negation)."""

import pathlib
from typing import Any, Callable

import pytest

from pathql.filters.stem import Stem


@pytest.mark.parametrize(
    "patterns, path, expected",
    [
        (["foo"], pathlib.Path("foo.txt"), True),
        (["bar"], pathlib.Path("foo.txt"), False),
        (["foo", "bar"], pathlib.Path("foo.txt"), True),
        (["foo", "bar"], pathlib.Path("bar.txt"), True),
        ("foo", pathlib.Path("foo.txt"), True),
        ("bar", pathlib.Path("foo.txt"), False),
        ("foo*", pathlib.Path("foo123.txt"), True),
        ("bar*", pathlib.Path("foo123.txt"), False),
    ],
)
def test_stem_match_patterns(patterns: Any, path: pathlib.Path, expected: bool):
    """Stem matches patterns, multiple, and wildcards."""
    # Arrange
    stem_filter = Stem(patterns)
    # Act
    result = stem_filter.match(path)
    # Assert
    assert result is expected


@pytest.mark.parametrize(
    "pattern, path, ignore_case, expected",
    [
        ("foo", pathlib.Path("FOO.txt"), False, False),
        ("foo", pathlib.Path("FOO.txt"), True, True),
        ("FOO", pathlib.Path("foo.txt"), False, False),
        ("FOO", pathlib.Path("foo.txt"), True, True),
    ],
)
def test_stem_case_sensitivity(pattern: str, path: pathlib.Path, ignore_case: bool, expected: bool):
    """Stem matches with/without case sensitivity."""
    # Arrange
    stem_filter = Stem(pattern, ignore_case=ignore_case)
    # Act
    result = stem_filter.match(path)
    # Assert
    assert result is expected


@pytest.mark.parametrize(
    "negate, pattern, path, expected",
    [
        (True, "foo", pathlib.Path("foo.txt"), False),
        (True, "bar", pathlib.Path("foo.txt"), True),
        (False, "foo", pathlib.Path("foo.txt"), True),
        (False, "bar", pathlib.Path("foo.txt"), False),
    ],
)
def test_stem_match_negation(negate: bool, pattern: str, path: pathlib.Path, expected: bool):
    """Stem negation works with _negate flag."""
    # Arrange
    stem_filter = Stem(pattern)
    stem_filter._negate = negate
    # Act
    result = stem_filter.match(path)
    # Assert
    assert result is expected


@pytest.mark.parametrize("patterns", [None, [], ""])
def test_stem_match_no_patterns_raises(patterns:Any):
    """Stem raises ValueError if no patterns are set."""
    # Arrange
    f = pathlib.Path("foo.txt")
    stem_filter = Stem(patterns)
    # Act & Assert
    with pytest.raises(ValueError):
        stem_filter.match(f)


@pytest.mark.parametrize(
    "s1, s2, expected",
    [
        (Stem("foo"), Stem("foo"), True),
        (Stem("foo"), Stem("bar"), False),
    ],
)
def test_stem_eq_and_ne_with_stem(s1:Stem, s2:Stem, expected:bool):
    """Stem equality and inequality with another Stem."""
    # Act & Assert
    assert (s1 == s2) is expected
    assert (s1 != s2) is (not expected)


@pytest.mark.parametrize(
    "op, opname",
    [
        (lambda s: s < "foo", "<"), # type: ignore
        (lambda s: s <= "foo", "<="), # type: ignore
        (lambda s: s > "foo", ">"), # type: ignore
        (lambda s: s >= "foo", ">="), # type: ignore
        (lambda s: s ^ "foo", "^"), # type: ignore
        (lambda s: s % "foo", "%"), # type: ignore
        (lambda s: s // "foo", "//"), # type: ignore
        (lambda s: s + "foo", "+"), # type: ignore
        (lambda s: s - "foo", "-"), # type: ignore
        (lambda s: s * "foo", "*"), # type: ignore
        (lambda s: s / "foo", "/"), # type: ignore
    ],
)
def test_stem_unsupported_operators(op: Callable[[Stem], Any], opname: str):
    """Stem raises NotImplementedError for unsupported operators."""
    # Arrange
    s = Stem()
    # Act & Assert
    try:
        op(s)
    except NotImplementedError:
        pass
    else:
        pytest.fail(f"Stem did not raise NotImplementedError for operator '{opname}'")