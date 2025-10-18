from enum import Enum, auto

class ResultField(Enum):
    SIZE = auto()
    MTIME = auto()
    CTIME = auto()
    ATIME = auto()
    MTIME_DT = auto()
    CTIME_DT = auto()
    ATIME_DT = auto()
    NAME = auto()
    SUFFIX = auto()
    STEM = auto()
    PATH = auto()
    PARENT = auto()
    PARENTS = auto()
    PARENTS_STEM_SUFFIX = auto()
