"""
Test Module: test_action_parallel_edge.py

Purpose:
--------
Edge case and robustness tests for apply_action parallelism:
- Zero files
- More workers than files
- Target directory usage
"""
import time
import pathlib
import shutil
import pytest
from pathql.actions.file_actions import FileActionResult, apply_action

DELAY_MS = 100
DELAY_SEC = DELAY_MS / 1000.0
OVERHEAD_ESTIMATE = 0.02  # 20ms

def delay_action(path: pathlib.Path, target_dir: pathlib.Path | None):
    time.sleep(DELAY_SEC)

@pytest.mark.parametrize("num_files, num_workers", [
    (0, 3),
    (1, 4),
    (5, 10),
])
def test_parallel_edge_cases(tmp_path: pathlib.Path, num_files: int, num_workers: int):
    # Arrange: Create dummy files
    files = [tmp_path / f"file_{i}.txt" for i in range(num_files)]
    for f in files:
        f.write_text("test")
    threshold = OVERHEAD_ESTIMATE * 2

    # Act: Run with more workers than files
    result = apply_action(files, delay_action, workers=num_workers)
    elapsed = result.total_time

    # Assert: All files processed
    assert set(result.success) == set(files)
    assert all(f in result.timings for f in files)
    for f in files:
        assert result.timings[f] >= DELAY_SEC, (
            f"File {f} timing too short: {result.timings[f]:.3f}s"
        )
    # Assert: Zero files case
    if num_files == 0:
        assert elapsed >= 0.0
        assert result.success == []
        assert result.failed == []
        assert result.errors == {}
        assert result.timings == {}
    # Assert: Single-threaded time should be > files * delay
    if num_files > 0 and num_workers == 1:
        assert elapsed > DELAY_SEC * num_files * 0.9


def copy_action(src: pathlib.Path, target_dir: pathlib.Path | None):
    if target_dir is not None:
        shutil.copy2(str(src), str(target_dir / src.name))


def test_parallel_target_dir(tmp_path: pathlib.Path):
    # Arrange: Create files and target dir
    files = [tmp_path / f"file_{i}.txt" for i in range(3)]
    for f in files:
        f.write_text(f.name)
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Act: Run copy_action in parallel
    result = apply_action(files, copy_action, target_dir=target_dir, workers=3)

    # Assert: All files copied and contain their filename
    for f in files:
        copied = target_dir / f.name
        assert copied.exists()
        assert copied.read_text() == f.name
    assert set(result.success) == set(files)
    assert result.total_time >= 0.0
