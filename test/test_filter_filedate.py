"""
Tests for the FileDate filter object.
Verifies operator overloads and correct extraction of file dates from stat and filename.
"""

import datetime
import pathlib
import sys

import pytest

from pathql.filters.between import Between
from pathql.filters.filedate import FileDate
from pathql.filters.stat_proxy import StatProxy

if sys.platform == "win32":
    BasePath = pathlib.WindowsPath
else:
    BasePath = pathlib.PosixPath

class DummyPath(BasePath):
    """A dummy Path subclass for testing with custom stat and stem."""
    def __new__(cls, *args, **kwargs):
        return BasePath.__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self._stat = kwargs.get("stat", None)
        self._stem = kwargs.get("stem", None)

    def stat(self):
        return self._stat

    @property
    def stem(self):
        return self._stem if self._stem is not None else super().stem

class DummyStat:
    """Dummy stat result for testing."""
    def __init__(self, mtime, ctime, atime):
        self.st_mtime = mtime
        self.st_ctime = ctime
        self.st_atime = atime

@pytest.fixture
def dummy_times():
    # Arrange

    # Jan 1, 2024
    dt1 = datetime.datetime(2024, 1, 1, 0, 0, 0)
    # Feb 1, 2024
    dt2 = datetime.datetime(2024, 2, 1, 0, 0, 0)
    # Mar 1, 2024
    dt3 = datetime.datetime(2024, 3, 1, 0, 0, 0)
    return dt1, dt2, dt3

def test_filedate_modified(dummy_times):
    """
    Test FileDate.modified operator overloads.
    """
    # Arrange

    dt1, dt2, dt3 = dummy_times
    stat = DummyStat(mtime=dt2.timestamp(), ctime=dt1.timestamp(), atime=dt3.timestamp())
    path = DummyPath("dummy.txt", stat=stat)
    fmod = FileDate().modified

    # Act

    actual_gt = (fmod > dt1).match(path, StatProxy(path))
    actual_ge = (fmod >= dt2).match(path, StatProxy(path))
    actual_lt = (fmod < dt1).match(path, StatProxy(path))
    actual_le = (fmod <= dt2).match(path, StatProxy(path))
    actual_eq = (fmod == dt2).match(path, StatProxy(path))
    actual_ne = (fmod != dt1).match(path, StatProxy(path))

    # Assert

    assert actual_gt
    assert actual_ge
    assert not actual_lt
    assert actual_le
    assert actual_eq
    assert actual_ne

def test_filedate_created(dummy_times):
    """
    Test FileDate.created operator overloads.
    """
    # Arrange

    dt1, dt2, dt3 = dummy_times
    stat = DummyStat(mtime=dt2.timestamp(), ctime=dt1.timestamp(), atime=dt3.timestamp())
    path = DummyPath("dummy.txt", stat=stat)
    fcre = FileDate().created

    # Act

    actual_lt = (fcre < dt2).match(path, StatProxy(path))
    actual_le = (fcre <= dt1).match(path, StatProxy(path))
    actual_eq = (fcre == dt1).match(path, StatProxy(path))
    actual_ne = (fcre != dt2).match(path, StatProxy(path))
    actual_gt = (fcre > dt2).match(path, StatProxy(path))

    # Assert

    assert actual_lt
    assert actual_le
    assert actual_eq
    assert actual_ne
    assert not actual_gt

def test_filedate_accessed(dummy_times):
    """
    Test FileDate.accessed operator overloads.
    """
    # Arrange

    dt1, dt2, dt3 = dummy_times
    stat = DummyStat(mtime=dt2.timestamp(), ctime=dt1.timestamp(), atime=dt3.timestamp())
    path = DummyPath("dummy.txt", stat=stat)
    facc = FileDate().accessed

    # Act

    actual_gt = (facc > dt2).match(path, StatProxy(path))
    actual_ge = (facc >= dt3).match(path, StatProxy(path))
    actual_eq = (facc == dt3).match(path, StatProxy(path))
    actual_ne = (facc != dt2).match(path, StatProxy(path))
    actual_lt = (facc < dt2).match(path, StatProxy(path))

    # Assert

    assert actual_gt
    assert actual_ge
    assert actual_eq
    assert actual_ne
    assert not actual_lt

def test_filedate_filename(dummy_times):
    """
    Test FileDate.filename operator overloads.
    """
    # Arrange

    dt1, dt2, dt3 = dummy_times
    # Filename: "2024-02-01_log.txt"
    path = DummyPath("2024-02-01_log.txt", stem="2024-02-01_log")
    ffile = FileDate().filename

    # Act

    actual_gt = (ffile > dt1).match(path, StatProxy(path))
    actual_ge = (ffile >= dt2).match(path, StatProxy(path))
    actual_eq = (ffile == dt2).match(path, StatProxy(path))
    actual_ne = (ffile != dt1).match(path, StatProxy(path))
    actual_lt = (ffile < dt1).match(path, StatProxy(path))

    # Assert

    assert actual_gt
    assert actual_ge
    assert actual_eq
    assert actual_ne
    assert not actual_lt

def test_filedate_between(dummy_times):
    """
    Test FileDate 'between' logic using two comparisons (lower inclusive, upper exclusive).
    """
    # Arrange

    dt1, dt2, dt3 = dummy_times
    stat = DummyStat(mtime=dt2.timestamp(), ctime=dt1.timestamp(), atime=dt3.timestamp())
    path = DummyPath("dummy.txt", stat=stat)
    fmod = FileDate().modified

    # Act

    between = (fmod >= dt1) & (fmod < dt3)

    actual_between = between.match(path, StatProxy(path))

    not_between = (fmod > datetime.datetime(2024, 2, 2)) & (fmod < dt3)
    actual_not_between = not_between.match(path, StatProxy(path))

    # Assert

    assert actual_between
    assert not actual_not_between

@pytest.fixture
def between_times():
    # Arrange

    # Dec 1, 2024
    dt1 = datetime.datetime(2024, 12, 1, 0, 0, 0)
    # Dec 15, 2024
    dt2 = datetime.datetime(2024, 12, 15, 0, 0, 0)
    # Dec 31, 2024
    dt3 = datetime.datetime(2024, 12, 31, 0, 0, 0)
    # Jan 1, 2025
    dt4 = datetime.datetime(2025, 1, 1, 0, 0, 0)
    return dt1, dt2, dt3, dt4

def test_filedate_between_operator(between_times):
    """
    Test the Between operator for FileDate filters.
    """
    # Arrange

    dt1, dt2, dt3, dt4 = between_times
    stat = DummyStat(mtime=dt2.timestamp(), ctime=dt1.timestamp(), atime=dt3.timestamp())
    path = DummyPath("dummy.txt", stat=stat)
    fmod = FileDate().modified

    # Act

    # Should match: dt2 is between dt1 and dt3
    between_filter = Between(fmod, dt1, dt3)
    actual_between = between_filter.match(path, StatProxy(path))

    # Should not match: dt2 is not between dt3 and dt4
    not_between_filter = Between(fmod, dt3, dt4)
    actual_not_between = not_between_filter.match(path, StatProxy(path))

    # Assert

    assert actual_between
    assert not actual_not_between
    