import pathlib
from src.pathql.filters.fileext import FileExt

def test_fileext_match():
    assert FileExt(["txt"]).match(pathlib.Path("foo.txt"))
    assert not FileExt(["png"]).match(pathlib.Path("foo.txt"))
