from pathql.filters.stat_proxy import StatProxy
import pathlib

class ProxyNotNeededTriggersExceptionOnUsage(StatProxy):
    """
    Dummy StatProxy for filters that do not require stat access.
    Any attempt to call .stat() will raise an exception, making it obvious
    that stat was not needed or should not be used in this context.
    """

    def __init__(self, path:pathlib.Path|None=None):
        self.path = path

    def stat(self):
        raise RuntimeError(
            "ProxyNotNeededTriggersExceptionOnUsage: stat() called on a filter that doesn't need stat()."
        )
