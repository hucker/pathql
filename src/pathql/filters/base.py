import pathlib
from typing import Any, Callable




class Filter:
    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)

    def __invert__(self):
        return NotFilter(self)

    def match(self, path: 'pathlib.Path', now=None, stat_result=None) -> bool:
        raise NotImplementedError




class AndFilter(Filter):
    def __init__(self, left: Filter, right: Filter):
        self.left = left
        self.right = right
    def match(self, path: 'pathlib.Path', now=None, stat_result=None) -> bool:
        return self.left.match(path, now=now, stat_result=stat_result) and self.right.match(path, now=now, stat_result=stat_result)




class OrFilter(Filter):
    def __init__(self, left: Filter, right: Filter):
        self.left = left
        self.right = right
    def match(self, path: 'pathlib.Path', now=None, stat_result=None) -> bool:
        return self.left.match(path, now=now, stat_result=stat_result) or self.right.match(path, now=now, stat_result=stat_result)




class NotFilter(Filter):
    def __init__(self, operand: Filter):
        self.operand = operand
    def match(self, path: 'pathlib.Path', now=None, stat_result=None) -> bool:
        return not self.operand.match(path, now=now, stat_result=stat_result)
