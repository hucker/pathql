"""
Pytest-based CLI integration tests for pathql.

This module sets up a temporary directory with test files and verifies CLI output for various file patterns.
"""

import sys
import os
import pathlib
from typing import Set, Generator
from unittest.mock import patch


from _pytest.capture import CaptureFixture
import pytest
from pathql.__main__ import main


@pytest.fixture
def test_dir_fixture(tmp_path: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    """Create and yield a temporary test directory with sample files."""
    d = tmp_path / "testdir"
    d.mkdir()
    (d / "foo.txt").write_text("foo")
    (d / "bar.py").write_text("bar")
    (d / "baz.md").write_text("baz")
    (d / "foo2.txt").write_text("foo2")
    yield d
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
    """Test CLI output for various file patterns in the test directory."""
    test_dir = test_dir_fixture
    with patch.object(sys, "argv", ["pathql", pattern, "-r"]):
        old_cwd = os.getcwd()
        try:
            os.chdir(test_dir)
            main()
        finally:
            os.chdir(old_cwd)
    captured = capsys.readouterr()
    found = {
        pathlib.Path(line).name
        for line in captured.out.strip().splitlines()
        if line and not line.startswith("PathQL")
    }
    assert found == expected
    found = {
        pathlib.Path(line).name
        for line in captured.out.strip().splitlines()
        if line and not line.startswith("PathQL")
    }
    assert found == expected
    assert "PathQL v" in captured.out
