from .base import Filter


class Between(Filter):
    """
    Filter that matches if a value is between two bounds: inclusive on the lower bound, exclusive on the upper bound.

    Usage:
        Between(AgeHours, 2, 3)  # Equivalent to (AgeHours >= 2) & (AgeHours < 3)

    This matches values x such that lower <= x < upper.
    """
    def __init__(self, filter_cls, lower, upper):
        self.filter = (filter_cls >= lower) & (filter_cls < upper)
    def match(self, path, now=None, stat_result=None):
        return self.filter.match(path, now=now, stat_result=stat_result)
