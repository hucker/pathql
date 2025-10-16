import pathlib
import time
import os
from pathql.filters.age import AgeMinutes, AgeDays, AgeYears

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

def test_age_fractional(tmp_path):
    f = tmp_path / "frac.txt"
    f.write_text("F")
    now = time.time()
    # 90 minutes ago
    os.utime(f, (now - 90 * 60, now - 90 * 60))
    # Should be 1.5 hours, or 1.5/24 days, or 1.5/24/365.25 years
    assert (AgeMinutes > 89).match(f, now=now)
    assert (AgeMinutes < 91).match(f, now=now)
    assert (AgeDays > (1.5/24 - 0.01)).match(f, now=now)
    assert (AgeDays < (1.5/24 + 0.01)).match(f, now=now)
    assert (AgeYears > (1.5/24/365.25 - 0.0001)).match(f, now=now)
    assert (AgeYears < (1.5/24/365.25 + 0.0001)).match(f, now=now)
