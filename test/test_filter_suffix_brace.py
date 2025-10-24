import pathlib

from pathql.filters.suffix import Suffix
from pathql.query import StatProxy


def test_suffix_brace_ignores_empty_entry(tmp_path: pathlib.Path) -> None:
    """Brace expansion should ignore empty entries like '{foo,,fum}'."""
    f1 = tmp_path / "a.foo"
    f1.write_text("x")
    f2 = tmp_path / "b.fum"
    f2.write_text("x")
    f3 = tmp_path / "c."  # would match empty extension if allowed
    f3.write_text("x")

    s = Suffix("{foo,,fum}")

    assert s.match(f2, StatProxy(f2))
    assert not s.match(f3, StatProxy(f3))
    assert not s.match(f3, StatProxy(f3))
