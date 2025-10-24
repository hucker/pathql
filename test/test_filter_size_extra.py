"""Extra tests for Size filter: errors and operator overloads."""

import pathlib

from pathql.filters.stat_proxy import StatProxy

import pytest

from pathql.filters.size import Size


def make_file(tmp_path: pathlib.Path, size: int = 1) -> pathlib.Path:
    """Create a file with the specified size in bytes."""
    file = tmp_path / "a_file.txt"
    file.write_bytes(b"x" * size)
    return file


def test_size_basic(tmp_path: pathlib.Path) -> None:
    """Basic Size filter logic is correct."""
    # Arrange
    file = make_file(tmp_path, 100)

    # Act and Assert
    assert Size(lambda x, y: x == y, 100).match(file, StatProxy(file))
    assert Size(lambda x, y: x < y, 200).match(file, StatProxy(file))
    assert not Size(lambda x, y: x > y, 200).match(file, StatProxy(file))


def test_size_error() -> None:
    """Size filter handles stat errors and missing value types gracefully."""
    # Act and Assert
    path = pathlib.Path("a_file.txt")
    assert Size(lambda x, y: x < y, 1).match(path, StatProxy(path)) is False
    with pytest.raises(TypeError):
        Size().match(path, StatProxy(path))


def test_size_operator_overloads(tmp_path: pathlib.Path) -> None:
    """Operator overloads produce expected filters and comparisons."""
    # Arrange
    file = make_file(tmp_path, 50)

    # Act and Assert
    assert Size() <= 100
    assert Size() < 1000
    assert Size() >= 10
    assert Size() > 1
    assert Size() == 50
    assert Size() != 51
    assert Size(lambda x, y: x == y, 50).match(file, StatProxy(file))
    assert Size() == 50
    assert Size() != 51
    assert Size(lambda x, y: x == y, 50).match(file, StatProxy(file))
