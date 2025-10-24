from pathql.filters.stat_proxy import StatProxy


class ProxyNotNeededTriggersExceptionOnUsage(StatProxy):
    """
    Dummy StatProxy for filters that do not require stat access.
    Any attempt to call .stat() will raise an exception, making it obvious
    that stat was not needed or should not be used in this context.
    """

    def __init__(self, path=None):
        self.path = path

    def stat(self):
        raise RuntimeError(
            "ProxyNotNeededTriggersExceptionOnUsage: stat() was called on a filter that should not require stat access."
        )
        raise RuntimeError(
            "ProxyNotNeededTriggersExceptionOnUsage: stat() was called on a filter that should not require stat access."
        )
