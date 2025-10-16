import pathlib
from src.pathql.filters.name import Name

def test_name_regex():
    assert Name(r"foo.*").match(pathlib.Path("foo123.txt"))
    assert not Name(r"bar.*").match(pathlib.Path("foo123.txt"))
