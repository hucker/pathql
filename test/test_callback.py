import pathlib

import pytest

from pathql.filters import MatchCallback, PathCallback
from pathql.filters.stat_proxy import StatProxy


def get_stat_proxy(path):
    return StatProxy(path)


def test_path_callback_positional_binding(tmp_path: pathlib.Path) -> None:
    """PathCallback can bind positional args for user callbacks."""
    # Arrange
    p = tmp_path / "photo.jpg"
    p.write_text("x")

    def exif_callback(path, tag, value) -> bool:
        """Return True when a supported tag/value pair is seen."""
        return tag == "Mfg" and value == "Canon"

    factory = PathCallback(exif_callback)
    bound = factory("Mfg", "Canon")

    # Act / Assert
    assert bound.match(p, get_stat_proxy(p))


def test_path_callback_keyword_binding(tmp_path: pathlib.Path) -> None:
    """PathCallback can bind keyword args for user callbacks."""
    # Arrange
    p = tmp_path / "photo2.jpg"
    p.write_text("x")

    def exif_callback(path, tag, value) -> bool:
        """Return True when a supported tag/value pair is seen."""
        return tag == "Mfg" and value == "Canon"

    factory = PathCallback(exif_callback)
    bound = factory(tag="Mfg", value="Canon")

    # Act / Assert
    assert bound.match(p, get_stat_proxy(p))


def test_path_callback_args_and_kwargs_merge(tmp_path: pathlib.Path) -> None:
    """PathCallback merges previously bound args with newly provided ones."""
    # Arrange
    p = tmp_path / "photo3.jpg"
    p.write_text("x")

    def exif_callback(path, tag, value) -> bool:
        return tag == "Mfg" and value == "Canon"

    factory = PathCallback(exif_callback, "Mfg")
    bound = factory("Canon")

    # Act / Assert
    assert bound.match(p, get_stat_proxy(p))


def test_path_callback_docstring_includes_func_doc_and_bound_args() -> None:
    """Instance docstring includes the wrapped function doc and bound args."""

    # Arrange
    def exif_callback(path, tag, value) -> bool:
        """Check EXIF tag and value."""
        return True

    factory = PathCallback(exif_callback)

    # Act
    bound = factory("Mfg", "Canon")

    # Assert
    # function doc should be included
    assert "Check EXIF tag and value." in (factory.__doc__ or "")
    # class __init__ and match docs should be included on instances
    assert "Create a PathCallback that binds positional and keyword args." in (
        bound.__doc__ or ""
    )
    assert "Call the callback with path and the configured args/kwargs." in (
        bound.__doc__ or ""
    )
    # bound args should be present
    assert "Bound arguments" in (bound.__doc__ or "")
    assert "'Mfg'" in (bound.__doc__ or "")


def test_unexpected_keyword_raises() -> None:
    """Supplying an unexpected keyword at construction raises TypeError."""

    # Arrange
    def cb(path, tag, value):
        return True

    # Act / Assert
    with pytest.raises(TypeError):
        PathCallback(cb, unexpected=1)


def test_keyword_only_required_raises() -> None:
    """Missing required keyword-only args raise at construction."""

    # Arrange
    def cb(path, *, flag):
        return flag

    # Act / Assert
    with pytest.raises(TypeError):
        PathCallback(cb)

    # Act / Assert (works when provided)
    p = pathlib.Path(".")
    assert PathCallback(cb, flag=True).match(p, get_stat_proxy(p))


def test_varargs_acceptance(tmp_path: pathlib.Path) -> None:
    """Callbacks with *args accept empty or provided extra args."""
    # Arrange
    p = tmp_path / "v.txt"
    p.write_text("x")

    def cb(path, *rest):
        return len(rest) > 0

    # Act / Assert
    assert PathCallback(cb).match(p, get_stat_proxy(p)) is False
    assert PathCallback(cb, 1).match(p, get_stat_proxy(p)) is True


def test_match_callback_invocation_and_docstring(tmp_path: pathlib.Path) -> None:
    """MatchCallback passes path, now and stat_result and composes docstring."""
    # Arrange
    p = tmp_path / "m.txt"
    p.write_text("x")

    def cb(path, now, stat_proxy) -> bool:
        """A callback that inspects now and stat_result."""
        # ensure now is present (may be None in tests) and stat_result is an os.stat_result-like
        stat_result = stat_proxy.stat_result if stat_proxy is not None else None
        return path.exists() and (
            stat_result is None or hasattr(stat_result, "st_mtime")
        )

    factory = MatchCallback(cb)
    bound = factory()

    # Act / Assert
    assert bound.match(p, get_stat_proxy(p), now=None) is True
    # docstring contains wrapped func doc and class docs
    assert "A callback that inspects now and stat_result." in (bound.__doc__ or "")
    assert (
        "Call the callback with (path, now, stat_result, *bound_args, **bound_kwargs)."
        in (bound.__doc__ or "")
    )


def test_match_callback_signature_enforcement() -> None:
    """MatchCallback rejects callables that don't accept path, now, stat_result."""

    def short_cb(path, now):
        return True

    with pytest.raises(TypeError):
        MatchCallback(short_cb)


def test_path_vs_match_callback_now_and_stat(tmp_path: pathlib.Path) -> None:
    """PathCallback ignores now/stat while MatchCallback receives them."""
    # Arrange
    p = tmp_path / "compare.txt"
    p.write_text("x")

    seen = {}

    def path_only(path):
        seen["path_only"] = True
        return True

    def full_sig(path, now, stat_proxy):
        stat_result = stat_proxy.stat_result if stat_proxy is not None else None
        seen["full_sig"] = (now is None) is False or stat_result is not None
        return True

    # Act
    assert PathCallback(path_only).match(p, get_stat_proxy(p), now=None) is True
    assert MatchCallback(full_sig).match(p, get_stat_proxy(p), now=None) is True

    # Assert
    assert "path_only" in seen
    assert "full_sig" in seen
