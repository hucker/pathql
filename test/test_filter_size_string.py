"""Exhaustive, parameterized tests for size parsing and operator overloads.

Follows AI_CONTEXT.md: AAA structure and clear Arrange/Act/Assert sections.
"""

import pathlib

import pytest

from pathql.filters.size import Size, parse_size


@pytest.mark.parametrize(
    "inp, expected",
    [
        (1024, 1024),
        (1.0, 1),
        (1.5, 1),  # floats are truncated to int(bytes)
        # SI units (decimal)
        ("1 b", 1),
        ("1B", 1),
        ("1 kb", 1000),
        ("1 KB", 1000),
        ("1 k", 1000),
        ("1 kb ", 1000),
        ("1.5 kb", int(1.5 * 1000)),
        ("2MB", 2 * 1000 * 1000),
        ("2 mb", 2 * 1000 * 1000),
        ("1 m", 1000**2),
        ("1 g", 1000**3),
        ("1 t", 1000**4),
        ("1 p", 1000**5),
        # IEC units (binary)
        ("1 KiB", 1024),
        ("1 KiB ", 1024),
        ("1 kib", 1024),
        ("1.5 KiB", int(1.5 * 1024)),
        ("3 MiB", 3 * 1024 * 1024),
        ("1 mib", 1024**2),
        ("1 gib", 1024**3),
        ("1 tib", 1024**4),
        ("1 pib", 1024**5),
        # no unit means bytes
        ("42", 42),
    ],
)
def test_parse_valid_values(
    inp: object,
    expected: int,
) -> None:
    """Valid size representations parse to expected byte counts."""
    # Arrange/Act
    got = parse_size(inp)

    # Assert
    assert isinstance(got, int)
    assert got == expected, f"Parsing {inp!r} -> {got}, expected {expected}"


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("1 PB", 1 * 1000**5),
        ("1 PiB", 1 * 1024**5),
        ("1 EB", 1 * 1000**6),
        # very large floats
        ("1.5 PB", int(1.5 * 1000**5)),
    ],
)
def test_parse_very_large_units(
    inp: object,
    expected: int,
) -> None:
    """Very large unit values parse correctly to bytes."""
    # Arrange/Act
    got = parse_size(inp)

    # Assert
    assert isinstance(got, int)
    assert got == expected


@pytest.mark.parametrize("bad", ["ten kb", "1 XB", "", "kb", "1.2.3 kb"])
def test_parse_invalid_strings_raise(bad: str) -> None:
    """Invalid size strings raise ValueError."""
    # Act/Assert
    with pytest.raises(ValueError):
        parse_size(bad)


@pytest.mark.parametrize("neg", [-1, -1.0, "-1 kb", "-1 KiB"])
def test_parse_negative_values_raise(neg: object) -> None:
    """Negative numeric sizes raise ValueError."""
    # Act/Assert
    with pytest.raises(ValueError):
        parse_size(neg)


@pytest.mark.parametrize(
    "file_size,op,operand,expected",
    [
        (2048, "__le__", "2 KiB", True),
        (2048, "__le__", "2 kb", False),  # 2 kb == 2000 bytes
        (2048, "__lt__", "3 KiB", True),
        (2048, "__gt__", "1 KiB", True),
        (1500, "__eq__", "1.5 kb", True),
        (1500, "__eq__", "1500", True),
    ],
)
def test_size_operator_with_various_units(
    tmp_path: pathlib.Path,
    file_size: int,
    op: str,
    operand: object,
    expected: bool,
) -> None:
    """Verify Size operator overloads handle different unit formats correctly."""
    # Arrange
    f = tmp_path / "f.txt"
    f.write_text("x" * file_size)
    s = Size()

    # Act
    result_filter = getattr(s, op)(operand)

    # Assert
    from pathql.filters.stat_proxy import StatProxy

    assert result_filter.match(f, StatProxy(f)) is expected


def test_size_operator_notimplemented_for_other_types() -> None:
    """Operator overloads return NotImplemented for unsupported operands."""
    # Arrange
    s = Size()

    # Act
    res = s.__lt__([1, 2, 3])

    # Assert
    assert res is NotImplemented
