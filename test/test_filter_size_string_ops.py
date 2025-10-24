"""Tests that ensure the Size operators accept string-like sizes and behave
the same as numeric operands.
"""

import pathlib

import pytest

from pathql.filters.size import Size, parse_size
from pathql.filters.stat_proxy import StatProxy


def test_size_ops_with_string_operands(size_test_folder: pathlib.Path) -> None:
    """Size operators accept string operands and behave like numeric ones."""
    # Arrange
    files = list(size_test_folder.iterdir())

    # Act / Assert - equality with plain number string and with explicit 'B'.
    assert any((Size() == "100").match(f, StatProxy(f)) for f in files)
    assert any((Size() == "200 B").match(f, StatProxy(f)) for f in files)

    # Act / Assert - inequality and comparisons using string operands
    assert all((Size() < "300").match(f, StatProxy(f)) for f in files)
    assert any((Size() <= "100").match(f, StatProxy(f)) for f in files)
    assert any((Size() >= "200").match(f, StatProxy(f)) for f in files)
    assert any((Size() > "100").match(f, StatProxy(f)) for f in files)


def test_size_eq_kib(tmp_path: pathlib.Path) -> None:
    """Compare a 1 KiB file using an IEC human-readable size string."""
    # Arrange - create a 1 KiB file
    p = tmp_path / "one_kib.bin"
    p.write_bytes(b"x" * 1024)
    # Act / Assert
    assert (Size() == "1 KiB").match(p, StatProxy(p))


def test_parse_size_unsupported_type_raises() -> None:
    """parse_size should raise TypeError for unsupported input types."""
    # Arrange
    bad_value = [1, 2, 3]

    # Act and Assert
    with pytest.raises(TypeError):
        parse_size(bad_value)
        parse_size(bad_value)
