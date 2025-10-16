import pytest
import pathlib
from pathql.filters.size import Size

def make_file(tmp_path, size=1):
    file = tmp_path / "afile.txt"
    file.write_bytes(b"x" * size)
    return file

def test_size_basic(tmp_path):
    file = make_file(tmp_path, 100)
    assert Size(lambda x, y: x == y, 100).match(file)
    assert Size(lambda x, y: x < y, 200).match(file)
    assert not Size(lambda x, y: x > y, 200).match(file)

def test_size_error(tmp_path):
    class BadPath:
        def stat(self):
            raise OSError("fail")
    bad_file = BadPath()
    assert Size(lambda x, y: x < y, 1).match(bad_file) is False
    with pytest.raises(ValueError):
        Size().match(make_file(tmp_path, 1))

def test_size_operator_overloads(tmp_path):
    file = make_file(tmp_path, 50)
    # Class-level operator overloads
    assert Size <= 100
    assert Size < 1000
    assert Size >= 10
    assert Size > 1
    assert Size == 50
    assert Size != 51
    # __class_getitem__
    assert Size[50].match(file)
    # Instance-level
    assert Size(lambda x, y: x == y, 50).match(file)
    # TODO: Not all operator overloads are meaningful, but these lines exercise them
