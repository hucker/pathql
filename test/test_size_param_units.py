"""Parameterized tests to ensure numeric and string size representations are equivalent.

This checks SI (1000**n) and IEC (1024**n) units across a range of magnitudes and
verifies both integer and decimal inputs behave as expected.
"""
import pathlib
import pytest

from pathql.filters.size import Size, parse_size


SIZES = [
    # (string form, numeric bytes)
    ("b", 1),
    ("kb", 1000),
    ("mb", 1000 ** 2),
    ("KiB", 1024),
    ("MiB", 1024 ** 2),
]


@pytest.mark.parametrize("unit,mult", SIZES)
def test_numeric_and_string_equivalents(tmp_path: pathlib.Path, unit: str, mult: int) -> None:
    # integer equality: 1 <unit> == mult bytes
    p = tmp_path / f"one_{unit}.bin"
    p.write_bytes(b"x" * mult)

    # Numeric operand
    assert (Size() == mult).match(p)

    # String operand, various casings and whitespace
    assert (Size() == f"1 {unit}").match(p)

    assert (Size() == f"1{unit}").match(p)
    assert (Size() == f"1 {unit.lower()}").match(p)


def test_large_unit_ranges(tmp_path: pathlib.Path):
    """Create a 1MB file and verify that larger unit filters (GB, TB, PB, etc.) are correct."""
    p = tmp_path / "one_mb.bin"
    p.write_bytes(b"x" * 1000**2)

    # Should be less than 1GB, 1TB, 1PB, etc.
    assert (Size() < "1 GB").match(p)
    assert (Size() < "1 TB").match(p)
    assert (Size() < "1 PB").match(p)
    assert (Size() < "1 EB").match(p)
    assert (Size() < "1 GiB").match(p)
    assert (Size() < "1 TiB").match(p)
    assert (Size() < "1 PiB").match(p)
    assert (Size() < "1 EiB").match(p)

    # Should be greater than 1KB, 1B
    assert (Size() > "1 KB").match(p)
    assert (Size() > "1 B").match(p)


@pytest.mark.parametrize("unit,mult", SIZES)
def test_decimal_string_values_truncate(tmp_path: pathlib.Path, unit: str, mult: int) -> None:
    # Create a file of size int(1.5 * mult)
    size = int(1.5 * mult)
    p = tmp_path / f"one_half_{unit}.bin"
    p.write_bytes(b"x" * size)

    # '1.5 <unit>' should truncate to int(1.5 * mult)
    assert (Size() == "1.5 " + unit).match(p)
    # parse_size should produce the same numeric value
    assert parse_size("1.5 " + unit) == size
