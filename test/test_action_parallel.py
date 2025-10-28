"""
====================
Test Module: test_action_parallel.py

Purpose:
--------
Verify that apply_action in file_actions.py achieves parallel speedup for IO-bound
tasks when using multiple workers. This test simulates IO-bound work with a delay
action and compares single-threaded and multi-threaded performance.

Test Structure:
---------------
1. Estimate overhead by running a no-op action on 5 files, 5 times.
2. Use a delay_action that sleeps for 100ms per file.
3. Create 5 dummy files in a temporary directory.
4. Run single-threaded and verify total time > 450ms.
5. Run with 5 workers and verify total time < 100ms + 2*overhead.
6. Validate that all files are processed and timings are recorded.

Rationale:
----------
This test demonstrates the effectiveness of parallelism for IO-bound workloads and
provides a benchmark for expected speedup. It also ensures that the parallel code
in apply_action is correct and thread-safe.
"""

import pathlib
import time

import pytest

from pathql.actions.file_actions import FileActionResult, apply_action

# Constants for delay action and overhead estimate
DELAY_MS = 100
DELAY_SEC = DELAY_MS / 1000.0
OVERHEAD_ESTIMATE = 0.02  # 20ms


def delay_action(path: pathlib.Path, target_dir: pathlib.Path | None):
    """
    Simulates IO-bound work by sleeping for DELAY_SEC.
    Args:
        path: Path to file (unused).
        target_dir: Target directory (unused).
    """
    time.sleep(DELAY_SEC)


@pytest.mark.parametrize("num_files", [5])
def test_parallel_speedup(tmp_path: pathlib.Path, num_files: int):
    """
    Verify parallel speedup for IO-bound tasks using apply_action.
    Arrange: Create dummy files and estimate overhead.
    Act: Run delay_action in single-threaded and multi-threaded modes.
    Assert: Check timing results and correctness of parallel execution.
    """
    # Arrange: Create dummy files
    files: list[pathlib.Path] = [tmp_path / f"file_{i}.txt" for i in range(num_files)]
    for f in files:
        f.write_text("test")

    # Arrange: Use a fixed overhead estimate for parallel threshold
    threshold = OVERHEAD_ESTIMATE * 2

    # Act: Single-threaded test with delay_action
    result: FileActionResult = apply_action(files, delay_action, workers=1)
    elapsed_single = result.total_time

    # Assert: Single-threaded should take at least DELAY_SEC * num_files
    assert elapsed_single > DELAY_SEC * num_files, (
        f"Single-threaded run too fast: {elapsed_single:.3f}s"
    )
    # Assert: All timings are >= DELAY_SEC
    for f in files:
        assert result.timings[f] >= DELAY_SEC, (
            f"File {f} timing too short: {result.timings[f]:.3f}s"
        )

    # Act: Parallel test with delay_action
    result: FileActionResult = apply_action(files, delay_action, workers=5)
    elapsed_parallel = result.total_time

    # Assert: Parallel should be much faster

    assert elapsed_parallel < DELAY_SEC + threshold, (
        f"Parallel run too slow: {elapsed_parallel:.3f}s, threshold={threshold:.3f}s"
    )
    # Assert: All files processed and timings recorded
    assert set(result.success) == set(files)
    assert all(f in result.timings for f in files)
    for f in files:
        assert result.timings[f] >= DELAY_SEC, (
            f"File {f} timing too short: {result.timings[f]:.3f}s"
        )
