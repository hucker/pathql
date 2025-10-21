import pathlib

import pytest

from pathql.filters import PathCallback


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
    assert bound.match(p)


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
    assert bound.match(p)


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
    assert bound.match(p)


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
    assert "Check EXIF tag and value." in (factory.__doc__ or "")
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
    assert PathCallback(cb, flag=True).match(pathlib.Path("."))


def test_varargs_acceptance(tmp_path: pathlib.Path) -> None:
    """Callbacks with *args accept empty or provided extra args."""
    # Arrange
    p = tmp_path / "v.txt"
    p.write_text("x")

    def cb(path, *rest):
        return len(rest) > 0

    # Act / Assert
    assert PathCallback(cb).match(p) is False
    assert PathCallback(cb, 1).match(p) is True