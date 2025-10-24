"""Testing for the access permission filters and their aliases."""

import pathlib
import sys
import typing

import pytest

from pathql.filters import Exec, Execute, Filter, RdWt, RdWtEx, Read, Write
from pathql.filters.stat_proxy import StatProxy


def get_stat_proxy(path):
    return StatProxy(path)


@pytest.fixture
def make_file(
    tmp_path: pathlib.Path,
) -> typing.Generator[typing.Callable[[str, bytes, bool], pathlib.Path], None, None]:
    """
    Fixture to create a file and clean up after the test.
    Usage:
        file_path = make_file(name, content=b"...", executable=True)
    """
    # Arrange
    created_files: list[pathlib.Path] = []

    def _make(
        name: str, content: bytes = b"test", executable: bool = False
    ) -> pathlib.Path:
        path = tmp_path / name
        path.write_bytes(content)
        if executable:
            if sys.platform == "win32":
                path = path.with_suffix(".exe")
                path.write_bytes(content)
            else:
                path.chmod(path.stat().st_mode | 0o111)
        created_files.append(path)
        return path

    yield _make

    # Teardown
    for f in created_files:
        try:
            f: pathlib.Path
            f.unlink()
        except Exception:
            pass


@pytest.mark.parametrize("filter_func", [Execute, Exec])
def test_executable_aliases(
    filter_func: type[Filter],
    make_file: typing.Callable[[str, bytes, bool], pathlib.Path],
) -> None:
    """
    Test Execute and Exec filters on an executable file.

    - Arrange: Create an executable file using the make_file fixture.
    - Act: Apply the filter to the file.
    - Assert: Verify that the filter matches the file.
    """
    # Arrange
    file_path = make_file("run_script", b"test", True)

    # Act and Assert
    try:
        assert filter_func().match(file_path, get_stat_proxy(file_path))
    except PermissionError:
        pytest.skip("Access denied for setting executable permission")


@pytest.mark.parametrize("filter_func", [Read, Write])
def test_read_write_aliases(
    filter_func: type[Filter],
    make_file: typing.Callable[[str, bytes, bool], pathlib.Path],
) -> None:
    """
    Test Read and Write filters on a regular file.

    - Arrange: Create a regular file using the make_file fixture.
    - Act: Apply the filter to the file.
    - Assert: Verify that the filter matches the file.
    """
    # Arrange
    file_path = make_file("rw_file", b"test", False)

    # Act and Assert
    try:
        assert filter_func().match(file_path, get_stat_proxy(file_path))
    except PermissionError:
        pytest.skip("Access denied for setting read/write permission")


def test_rdwt(make_file: typing.Callable[[str, bytes, bool], pathlib.Path]) -> None:
    """
    Test RdWt composite filter and class-level AND on a regular file.

    - Arrange: Create a regular file using the make_file fixture.
    - Act: Apply the RdWt filter and class-level AND to the file.
    - Assert: Verify that both filters match the file.
    """
    # Arrange
    file_path = make_file("rdwt_file", b"test", False)

    # Act and Assert
    try:
        # Instance composite
        assert RdWt().match(file_path, get_stat_proxy(file_path))
        # Instance-level AND
        assert (Read() & Write()).match(file_path, get_stat_proxy(file_path))
    except PermissionError:
        pytest.skip("Access denied for setting read/write permission")


def test_rdwt_ex(make_file: typing.Callable[[str, bytes, bool], pathlib.Path]) -> None:
    """
    Test RdWtEx composite filter and class-level AND chaining on an executable file.

    - Arrange: Create an executable file using the make_file fixture.
    - Act: Apply the RdWtEx filter and class-level AND chaining to the file.
    - Assert: Verify that both filters match the file.
    """
    # Arrange
    file_path = make_file("rdwtex_file", b"test", True)

    # Act and Assert
    try:
        # Instance composite
        assert RdWtEx().match(file_path, get_stat_proxy(file_path))
        # Instance-level AND chaining
        assert (Read() & Write() & Execute()).match(
            file_path, get_stat_proxy(file_path)
        )
    except PermissionError:
        pytest.skip("Access denied for setting permissions")
