import pathlib
from pathql.actions import zip_matches


def test_zip_matches_dry_run(tmp_path: pathlib.Path) -> None:
    # create some files
    d = tmp_path / "data"
    d.mkdir()
    f1 = d / "a.txt"
    f1.write_text("hello")
    f2 = d / "b.txt"
    f2.write_text("world")

    # dry run should return matches but not create the zip
    z = tmp_path / "out.zip"
    matches = zip_matches(d, lambda root: root.iterdir(), z, dry_run=True)
    assert set(matches) == {f1, f2}
    assert not z.exists()

