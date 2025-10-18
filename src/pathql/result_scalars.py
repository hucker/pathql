from enum import Enum, auto
import statistics

class ScalarAgg(Enum):
    COUNT = auto()
    MEAN = auto()
    MEDIAN = auto()
    MIN = auto()
    MAX = auto()
    MODE=auto()
    STDEV=auto()


def scalar_aggregate(values:list[int|float], agg: ScalarAgg):
    """
    Perform a scalar aggregation on a list of values.
    agg: ScalarAgg.COUNT, ScalarAgg.MEAN, ScalarAgg.MEDIAN, ScalarAgg.MIN, ScalarAgg.MAX
    """
    if agg == ScalarAgg.COUNT:
        return len(values)
    elif agg == ScalarAgg.MEAN:
        return statistics.mean(values) if values else None
    elif agg == ScalarAgg.MODE:
        return statistics.mode(values) if values else None
    elif agg == ScalarAgg.MEDIAN:
        return statistics.median(values) if values else None
    elif agg == ScalarAgg.STDEV:
        return statistics.stdev(values) if values else None
    elif agg == ScalarAgg.MIN:
        return min(values) if values else None
    elif agg == ScalarAgg.MAX:
        return max(values) if values else None
    else:
        raise ValueError(f"Unknown aggregation: {agg}")
