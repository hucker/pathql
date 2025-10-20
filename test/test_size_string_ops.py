"""Tests that ensure the Size operators accept string-like sizes and behave
the same as numeric operands.
"""
import pathlib
import pytest

from pathql.filters.size import Size, parse_size


def test_size_ops_with_string_operands(size_test_folder: pathlib.Path) -> None:
    files = list(size_test_folder.iterdir())

    # Equality with plain number string and with explicit 'B' suffix
    assert any((Size() == "100").match(f) for f in files)
    assert any((Size() == "200 B").match(f) for f in files)

    # Inequality and comparisons using string operands
    assert all((Size() < "300").match(f) for f in files)
    assert any((Size() <= "100").match(f) for f in files)
    assert any((Size() >= "200").match(f) for f in files)
    assert any((Size() > "100").match(f) for f in files)


def test_size_eq_kib(tmp_path: pathlib.Path) -> None:
    # create a 1 KiB file and compare using IEC string
    p = tmp_path / "one_kib.bin"
    p.write_bytes(b"x" * 1024)
    assert (Size() == "1 KiB").match(p)


def test_parse_size_unsupported_type_raises() -> None:
    with pytest.raises(TypeError):
        parse_size([1, 2, 3])
