import pathlib
from typing import Any, Callable

from .alias import StatProxyOrNone
from .base import Filter


class AttributeFilter(Filter):
    """
    Generic filter for extracting an attribute and comparing it.
    """

    def __init__(
        self,
        extractor: Callable[[pathlib.Path, StatProxyOrNone], Any],
        op: Callable[[Any, Any], bool],
        value: Any,
        requires_stat: bool = True,
    ):
        self.extractor = extractor
        self.op = op
        self.value = value
        self.requires_stat = requires_stat

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: Any = None,
    ) -> bool:
        if self.op is None or self.value is None:
            raise TypeError(f"{self.__class__.__name__} filter not fully specified.")
        if self.requires_stat and stat_proxy is None:
            raise ValueError(
                f"{self.__class__.__name__} filter requires stat_proxy, but none was provided."
            )
        try:
            attr = self.extractor(path, stat_proxy)
            return self.op(attr, self.value)
        except Exception:
            return False
        except Exception:
            return False
