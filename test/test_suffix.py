
import pathlib
import pytest
from pathql.filters.suffix import Suffix, Ext


@pytest.fixture(params=[Suffix, Ext])
def suffix_cls(request):
    return request.param

def test_suffix_eq(suffix_cls):
    # Should match a single extension using operator syntax
    f = pathlib.Path("foo.txt")
    assert (suffix_cls == "txt").match(f)
    assert not (suffix_cls == "md").match(f)

def test_suffix_multiple(suffix_cls):
    # Should match any of multiple extensions using operator syntax
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.md")
    suffix_filter = (suffix_cls == "txt") | (suffix_cls == "md")
    assert suffix_filter.match(f1)
    assert suffix_filter.match(f2)

def test_suffix_case_insensitive(suffix_cls):
    # Should match extensions case-insensitively using operator syntax
    f = pathlib.Path("foo.TXT")
    assert (suffix_cls == "txt").match(f)
    assert (suffix_cls == "TXT").match(f)

def test_suffix_no_extension(suffix_cls):
    # Should not match if the file has no extension using operator syntax
    f = pathlib.Path("foo")
    assert not (suffix_cls == "txt").match(f)

def test_suffix_operator_eq(suffix_cls):
    # Should support == operator for single extension (already covered above)
    f = pathlib.Path("foo.txt")
    assert (suffix_cls == "txt").match(f)
    assert not (suffix_cls == "md").match(f)

def test_suffix_operator_in(suffix_cls):
    # Should support 'in' operator for extension membership (using == syntax)
    f = pathlib.Path("foo.txt")
    assert ("txt" in (suffix_cls == "txt"))
    assert not ("md" in (suffix_cls == "txt"))

def test_suffix_whitespace_split(suffix_cls):
    # Should split a string on whitespace to match multiple extensions (constructor style still needed)
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.bmp")
    suffix_filter = suffix_cls("txt bmp")
    assert suffix_filter.match(f1)
    assert suffix_filter.match(f2)
    assert not suffix_filter.match(pathlib.Path("baz.md"))

def test_suffix_nosplit(suffix_cls):
    # Should treat the string as a single extension if nosplit=True (constructor style still needed)
    f = pathlib.Path("foo.txt bmp")
    suffix_filter = suffix_cls("txt bmp", nosplit=True)
    assert suffix_filter.match(f)
    suffix_filter2 = suffix_cls("txt bmp")
    assert not suffix_filter2.match(f)
