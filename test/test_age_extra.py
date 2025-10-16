"""Extra tests for AgeDays and AgeYears filters, including error handling and edge cases."""

import pytest
import pathlib
import time
from pathql.filters.age import AgeDays, AgeYears

def make_file(tmp_path):
    file = tmp_path / "afile.txt"
    file.write_text("x")
    return file

def test_agedays_basic(tmp_path):
    file = make_file(tmp_path)
    now = time.time()
    # Should match age 0 days
    assert AgeDays(lambda x, y: x <= y, 1).match(file, now=now)
    # Age is exactly 0, so x > 0 is False, x >= 0 is True
    assert not AgeDays(lambda x, y: x < y, 0).match(file, now=now)

def test_agedays_error(tmp_path, monkeypatch):
    file = make_file(tmp_path)
    # Simulate stat error
    # TODO: Hard to test OSError branch without monkeypatching or a custom path object
    # Not fully specified
    with pytest.raises(ValueError):
        AgeDays().match(file)

def test_ageyears_basic(tmp_path):
    file = make_file(tmp_path)
    now = time.time()
    # Should match age 0 years
    assert AgeYears(lambda x, y: x <= y, 1).match(file, now=now)
    assert not AgeYears(lambda x, y: x < y, 0).match(file, now=now)

def test_ageyears_error(tmp_path, monkeypatch):
    file = make_file(tmp_path)
    # TODO: Hard to test OSError branch without monkeypatching or a custom path object
    with pytest.raises(ValueError):
        AgeYears().match(file)
