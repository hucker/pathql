import pathlib
import time
from .base import Filter


class AgeDays(Filter):
    def __init__(self, op=None, value=None):
        self.op = op
        self.value = value

    def match(self, path: 'pathlib.Path', now=None) -> bool:
        if self.op is None or self.value is None:
            raise ValueError("AgeDays filter not fully specified.")
        try:
            import time
            if now is None:
                now = time.time()
            age_d = (now - path.stat().st_mtime) / (60 * 60 * 24)
            return self.op(age_d, self.value)
        except Exception:
            return False

    def __le__(self, other):
        return AgeDays.__new__(AgeDays, lambda x, y: x <= y, other)
    def __lt__(self, other):
        return AgeDays.__new__(AgeDays, lambda x, y: x < y, other)
    def __ge__(self, other):
        return AgeDays.__new__(AgeDays, lambda x, y: x >= y, other)
    def __gt__(self, other):
        return AgeDays.__new__(AgeDays, lambda x, y: x > y, other)
    def __eq__(self, other):
        return AgeDays.__new__(AgeDays, lambda x, y: x == y, other)
    def __ne__(self, other):
        return AgeDays.__new__(AgeDays, lambda x, y: x != y, other)

class AgeYears(Filter):
    def __init__(self, op=None, value=None):
        self.op = op
        self.value = value

    def match(self, path: 'pathlib.Path', now=None) -> bool:
        if self.op is None or self.value is None:
            raise ValueError("AgeYears filter not fully specified.")
        try:
            import time
            if now is None:
                now = time.time()
            age_y = (now - path.stat().st_mtime) / (60 * 60 * 24 * 365.25)
            return self.op(age_y, self.value)
        except Exception:
            return False

    def __le__(self, other):
        return AgeYears.__new__(AgeYears, lambda x, y: x <= y, other)
    def __lt__(self, other):
        return AgeYears.__new__(AgeYears, lambda x, y: x < y, other)
    def __ge__(self, other):
        return AgeYears.__new__(AgeYears, lambda x, y: x >= y, other)
    def __gt__(self, other):
        return AgeYears.__new__(AgeYears, lambda x, y: x > y, other)
    def __eq__(self, other):
        return AgeYears.__new__(AgeYears, lambda x, y: x == y, other)
    def __ne__(self, other):
        return AgeYears.__new__(AgeYears, lambda x, y: x != y, other)


class AgeMinutes(Filter):
    def __init__(self, op=None, value=None):
        self.op = op
        self.value = value

    def match(self, path: 'pathlib.Path', now=None) -> bool:
        if self.op is None or self.value is None:
            raise ValueError("AgeMinutes filter not fully specified.")
        try:
            import time
            if now is None:
                now = time.time()
            age_m = (now - path.stat().st_mtime) / 60
            return self.op(age_m, self.value)
        except Exception:
            return False

    def __le__(self, other):
        return AgeMinutes.__new__(AgeMinutes, lambda x, y: x <= y, other)
    def __lt__(self, other):
        return AgeMinutes.__new__(AgeMinutes, lambda x, y: x < y, other)
    def __ge__(self, other):
        return AgeMinutes.__new__(AgeMinutes, lambda x, y: x >= y, other)
    def __gt__(self, other):
        return AgeMinutes.__new__(AgeMinutes, lambda x, y: x > y, other)
    def __eq__(self, other):
        return AgeMinutes.__new__(AgeMinutes, lambda x, y: x == y, other)
    def __ne__(self, other):
        return AgeMinutes.__new__(AgeMinutes, lambda x, y: x != y, other)
