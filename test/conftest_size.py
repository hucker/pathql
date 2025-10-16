import pytest
import pathlib

@pytest.fixture(scope="function")
def size_test_folder(tmp_path):
    """
    Create a folder with two files: 100.txt (100 bytes), 200.txt (200 bytes)
    """
    f1 = tmp_path / "100.txt"
    f2 = tmp_path / "200.txt"
    f1.write_bytes(b"A" * 100)
    f2.write_bytes(b"B" * 200)
    return tmp_path
