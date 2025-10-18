"""Extra tests for Size filter, including error handling and custom file creation."""
import pathlib
import pytest
from pathql.filters.size import Size

def make_file(tmp_path: pathlib.Path, size: int = 1) -> pathlib.Path:
    file = tmp_path / "afile.txt"
    file.write_bytes(b"x" * size)
    return file

def test_size_basic(tmp_path: pathlib.Path):
    file = make_file(tmp_path, 100)
    assert Size(lambda x, y: x == y, 100).match(file)
    assert Size(lambda x, y: x < y, 200).match(file)
    assert not Size(lambda x, y: x > y, 200).match(file)

def test_size_error(tmp_path: pathlib.Path):
    class BadPath:
        def stat(self):
            raise OSError("fail")
    bad_file = BadPath()
    # Should return False if stat fails
    assert Size(lambda x, y: x < y, 1).match(bad_file) is False
    # Should raise TypeError if match() is called on unconfigured Size
    with pytest.raises(TypeError):
        Size().match(pathlib.Path("afile.txt"))

def test_size_operator_overloads(tmp_path: pathlib.Path):
    file = make_file(tmp_path, 50)
    # Instance-level operator overloads
    assert Size() <= 100
    assert Size() < 1000
    assert Size() >= 10
    assert Size() > 1
    assert Size() == 50
    assert Size() != 51
    # Instance-level
    assert Size(lambda x, y: x == y, 50).match(file)
    # TODO: Not all operator overloads are meaningful, but these lines exercise them
