"""Path callback filter.

Allows users to create a Filter from a callable that accepts a Path and any
additional positional/keyword arguments. The returned object can be used as a
factory (bind args via __call__) and the instance docstring includes the
wrapped function's docstring plus the bound arguments.
"""
from __future__ import annotations

import inspect
import pathlib
from typing import Any, Callable

from .base import Filter
from .alias import DatetimeOrNone, StatResultOrNone

PathCallable = Callable[..., bool]


class PathCallback(Filter):
    """Call a user function with a Path and optional bound args/kwargs."""

    def __init__(self, func: PathCallable, *args: Any, **kwargs: Any) -> None:
        """Create a PathCallback that binds positional and keyword args."""
        if not callable(func):
            raise TypeError("func must be callable")
        self.func = func
        self.args = tuple(args)
        self.kwargs = dict(kwargs)

        # Compose instance docstring from wrapped function doc and bound args
        func_doc = inspect.getdoc(func) or ""
        bound_parts: list[str] = []
        if self.args:
            bound_parts.append(f"args={self.args!r}")
        if self.kwargs:
            bound_parts.append(f"kwargs={self.kwargs!r}")
        bound = ", ".join(bound_parts) if bound_parts else "no bound args"
        self.__doc__ = (func_doc + "\n\n" if func_doc else "") + f"Bound arguments: {bound}"

        # Try to capture signature for nicer errors (optional)
        try:
            sig = inspect.signature(func)
        except (TypeError, ValueError):
            # Builtins or uninspectable callables may raise; skip validation
            self._sig = None
            return

        self._sig = sig
        params = list(sig.parameters.values())

        # Ensure the callable accepts at least one positional argument (the path)
        pos_params = [
            p
            for p in params
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        var_positional = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)
        var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)

        if not pos_params and not var_positional:
            raise TypeError("callback must accept at least one positional argument for the path")

        # Do not require all positional parameters to be bound now (factory pattern).
        # Only ensure we haven't bound too many positional args.
        max_pos_after_path = max(0, len(pos_params) - 1)
        if not var_positional and len(self.args) > max_pos_after_path:
            raise TypeError(
                f"{func!r} accepts at most {max_pos_after_path} positional args after "
                f"the path, but {len(self.args)} were provided"
            )

        # Ensure bound keyword names are accepted by the callable or **kwargs is present.
        allowed_kw = {
            p.name
            for p in params
            if p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        }
        required_kwonly = [
            p.name
            for p in params
            if p.kind == inspect.Parameter.KEYWORD_ONLY and p.default is inspect.Parameter.empty
        ]
        missing_kwonly = [k for k in required_kwonly if k not in self.kwargs]
        if missing_kwonly:
            raise TypeError(f"{func!r} missing required keyword-only args: {missing_kwonly}")
        for key in self.kwargs:
            if key not in allowed_kw and not var_keyword:
                raise TypeError(f"{func!r} got unexpected keyword argument '{key}'")

    def __call__(self, *args: Any, **kwargs: Any) -> "PathCallback":
        """Return a new PathCallback with additional bound args/kwargs."""
        combined_args = (*self.args, *args)
        combined_kwargs = {**self.kwargs, **kwargs}
        return PathCallback(self.func, *combined_args, **combined_kwargs)

    def match(
        self,
        path: pathlib.Path,
        now: DatetimeOrNone = None,
        stat_result: StatResultOrNone = None,
    ) -> bool:
        """Call the callback with path and the configured args/kwargs."""
        try:
            return bool(self.func(path, *self.args, **self.kwargs))
        except TypeError as exc:
            name = getattr(self.func, "__name__", repr(self.func))
            raise TypeError(f"Callback {name!r} invocation failed: {exc}") from exc

    def __repr__(self) -> str:
        name = getattr(self.func, "__name__", repr(self.func))
        return f"PathCallback({name}, args={self.args!r}, kwargs={self.kwargs!r})"