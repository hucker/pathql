"""StatProxy subclass that raises if stat access is attempted (defensive tool for filters)."""

from .alias import PathOrNone
from .stat_proxy import StatProxy


class StatProxyGuard(StatProxy):
    """
    Defensive programming tool: a fake StatProxy for filters that do not require stat access.
    If any code attempts to use .stat(), this proxy will immediately raise an exception.
    This makes it clear that stat access is not needed and helps catch accidental or
    inappropriate stat usage early in development or testing.
    """

    def __init__(self, path: PathOrNone = None):  # pylint: disable=super-init-not-called
        self.path = path

    def stat(self):
        raise RuntimeError(
            "ProxyNotNeededTriggersExceptionOnUsage: stat() was called on a filter not needing stat"
        )
