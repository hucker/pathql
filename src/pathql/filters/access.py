"""
access.py

Portable file access permission filters for PathQL.

Provides filters for Read, Write, and Execute permissions using os.access.
Includes composite filters RdWt (read & write) and RdWtEx (read, write & execute).

These filters work across Unix and Windows, but note that 'executable' on Windows
is determined by file extension and access, not a permission bit.
"""

import os
import pathlib

from .alias import DatetimeOrNone
from .base import Filter


class Read(Filter):
    """
    Filter that matches if the file is readable by the current user.
    """

    def match(
        self,
        path: pathlib.Path,
        stat_proxy,
        now: DatetimeOrNone = None,
    ) -> bool:
        return os.access(path, os.R_OK)


class Write(Filter):
    """
    Filter that matches if the file is writable by the current user.
    """

    def match(
        self,
        path: pathlib.Path,
        stat_proxy,
        now: DatetimeOrNone = None,
    ) -> bool:
        return os.access(path, os.W_OK)


class Execute(Filter):
    """
    Filter that matches if the file is executable by the current user.
    """

    def match(
        self,
        path: pathlib.Path,
        stat_proxy,
        now: DatetimeOrNone = None,
    ) -> bool:
        return os.access(path, os.X_OK)


Exec = Execute


# Composite filters for convenience (instances)
def RdWt() -> Filter:
    """
    Composite filter: matches files that are both readable and writable by the current user.
    Equivalent to: Read & Write
    """
    return Read() & Write()


def RdWtEx() -> Filter:
    """
    Composite filter: matches files that are readable, writable, and executable by the current user.
    Equivalent to: Read & Write & Execute
    """
    return Read() & Write() & Execute()


# Instance-level composability for idiomatic usage
ReadWrite = Read() & Write()
ReadWriteExec = Read() & Write() & Execute()
ReadWrite = Read() & Write()
ReadWriteExec = Read() & Write() & Execute()
