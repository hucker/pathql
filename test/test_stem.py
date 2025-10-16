import pathlib
import pytest
from pathql.filters.stem import Stem, Name

import pytest

@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_eq(cls):
    f = pathlib.Path("foo.txt")
    assert cls(["foo"]).match(f)
    assert not cls(["bar"]).match(f)

@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_multiple(cls):
    f1 = pathlib.Path("foo.txt")
    f2 = pathlib.Path("bar.txt")
    stem_filter = cls(["foo", "bar"])
    assert stem_filter.match(f1)
    assert stem_filter.match(f2)

@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_string(cls):
    f = pathlib.Path("foo.txt")
    assert cls("foo").match(f)
    assert not cls("bar").match(f)

@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_regex(cls):
    f = pathlib.Path("foo123.txt")
    assert cls(r"foo.*").match(f)
    assert not cls(r"bar.*").match(f)

@pytest.mark.parametrize("cls", [Stem, Name])
def test_name_alias(cls):
    f = pathlib.Path("foo.txt")
    assert cls("foo").match(f)
    assert not cls("bar").match(f)

@pytest.mark.parametrize("cls", [Stem, Name])
def test_stem_regex_patterns(cls):
    # Match any stem starting with 'foo'
    assert cls(r"foo.*").match(pathlib.Path("foo123.txt"))
    assert cls(r"foo.*").match(pathlib.Path("foo.txt"))
    assert not cls(r"foo.*").match(pathlib.Path("barfoo.txt"))

    # Match any stem ending with digits
    assert cls(r".*\d$").match(pathlib.Path("file1.txt"))
    assert not cls(r".*\d$").match(pathlib.Path("fileA.txt"))

    # Match exact stem
    assert cls(r"^bar$").match(pathlib.Path("bar.txt"))
    assert not cls(r"^bar$").match(pathlib.Path("foobar.txt"))

    # Match stems with only lowercase letters (case-sensitive)
    assert cls(r"^[a-z]+$", ignore_case=False).match(pathlib.Path("abc.txt"))
    assert not cls(r"^[a-z]+$", ignore_case=False).match(pathlib.Path("Abc.txt"))
