import pathlib
import time
import os
from src.pathql.filters.age import AgeMinutes, AgeDays, AgeYears

def test_age_minutes(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("A")
    now = time.time()
    os.utime(f, (now - 600, now - 600))
    assert (AgeMinutes > 5).match(f, now=now)
    assert not (AgeMinutes < 5).match(f, now=now)

def test_age_days(tmp_path):
    f = tmp_path / "b.txt"
    f.write_text("B")
    now = time.time()
    os.utime(f, (now - 86400 * 2, now - 86400 * 2))
    assert (AgeDays > 1).match(f, now=now)
    assert not (AgeDays < 1).match(f, now=now)

def test_age_years(tmp_path):
    f = tmp_path / "c.txt"
    f.write_text("C")
    now = time.time()
    os.utime(f, (now - 365.25 * 86400 * 2, now - 365.25 * 86400 * 2))
    assert (AgeYears > 1).match(f, now=now)
    assert not (AgeYears < 1).match(f, now=now)
