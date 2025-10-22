import pathlib

from pathql.actions import delete_matches


def test_delete_matches_dry_run_and_actual(tmp_path: pathlib.Path) -> None:
    d = tmp_path / "data"
    d.mkdir()
    f1 = d / "a.txt"
    f1.write_text("1")
    f2 = d / "b.txt"
    f2.write_text("2")

    # dry run
    dry = delete_matches(d, lambda root: root.iterdir(), dry_run=True)
    assert set(dry) == {f1, f2}

    # actual delete
    deleted = delete_matches(d, lambda root: root.iterdir(), dry_run=False)
    assert set(deleted) == {f1, f2}
    assert not f1.exists() and not f2.exists()
    assert not f1.exists() and not f2.exists()
