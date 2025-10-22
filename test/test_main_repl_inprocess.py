"""
Pytest-based CLI integration tests for pathql.

This module sets up a temporary directory with test files and verifies
CLI output for various file patterns.
"""

import os
import pathlib
import sys
from typing import Generator, Set
from unittest.mock import patch

import pytest
from _pytest.capture import CaptureFixture

from pathql.__main__ import main


@pytest.fixture
def test_dir_fixture(tmp_path: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    """
    Create and yield a temporary test directory with sample files.

    - Arrange: Create a temporary directory and populate it with test files.
    - Act: Yield the directory for use in tests.
    - Assert: Clean up the directory after the test.
    """

    # Arrange
    d = tmp_path / "testdir"
    d.mkdir()
    (d / "foo.txt").write_text("foo")
    (d / "bar.py").write_text("bar")
    (d / "baz.md").write_text("baz")
    (d / "foo2.txt").write_text("foo2")

    # Act
    yield d

    # Teardown
    for f in d.iterdir():
        f.unlink()
    d.rmdir()


@pytest.mark.parametrize(
    "pattern,expected",
    [
        ("foo*", {"foo.txt", "foo2.txt"}),
        ("*.py", {"bar.py"}),
        ("*.md", {"baz.md"}),
        ("*", {"foo.txt", "foo2.txt", "bar.py", "baz.md"}),
    ],
)
def test_main_repl_inprocess_cli(
    test_dir_fixture: pathlib.Path,
    capsys: CaptureFixture[str],
    pattern: str,
    expected: Set[str],
) -> None:
    """
    Test CLI output for various file patterns in the test directory.

    - Arrange: Set up the test directory and mock CLI arguments.
    - Act: Run the main function and capture the output.
    - Assert: Verify that the output matches the expected file patterns.
    """
    # Arrange
    test_dir = test_dir_fixture
    with patch.object(sys, "argv", ["pathql", pattern, "-r"]):
        old_cwd = os.getcwd()
        try:
            os.chdir(test_dir)

            # Act
            main()
        finally:
            os.chdir(old_cwd)

    # Assert
    captured = capsys.readouterr()
    found = {
        pathlib.Path(line).name
        for line in captured.out.strip().splitlines()
        if line and not line.startswith("PathQL")
    }
    assert found == expected
    assert "PathQL v" in captured.out
    assert "PathQL v" in captured.out
