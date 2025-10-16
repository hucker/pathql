import pathlib
from typing import Any, Callable


class Filter:
    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)

    def __invert__(self):
        return NotFilter(self)

    def match(self, path: 'pathlib.Path') -> bool:
        raise NotImplementedError


class AndFilter(Filter):
    def __init__(self, left: Filter, right: Filter):
        self.left = left
        self.right = right
    def match(self, path: 'pathlib.Path') -> bool:
        return self.left.match(path) and self.right.match(path)


class OrFilter(Filter):
    def __init__(self, left: Filter, right: Filter):
        self.left = left
        self.right = right
    def match(self, path: 'pathlib.Path') -> bool:
        return self.left.match(path) or self.right.match(path)


class NotFilter(Filter):
    def __init__(self, operand: Filter):
        self.operand = operand
    def match(self, path: 'pathlib.Path') -> bool:
        return not self.operand.match(path)
