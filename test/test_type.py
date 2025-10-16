import pathlib
from src.pathql.filters.type import Type

def test_type_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("A")
    assert (Type == Type.FILE).match(f)

def test_type_directory(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    assert (Type == Type.DIRECTORY).match(d)
