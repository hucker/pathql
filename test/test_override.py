"""
Test for a simple overridden custom filter.

Strictly speaking this isn't really required since we use this method in other tests, but they
typically just return true/false for test purposes.  This test demonstrates a more realistic
use case where we access the contents of a file for the test.
"""

import json
import pathlib

import pytest

from pathql.filters.alias import DatetimeOrNone, StatProxyOrNone
from pathql.filters.base import Filter


class JsonKeyValueFilter(Filter):
    """Filter that matches a specific key/value pair in a JSON file."""

    def __init__(self, key: str, value: str):
        self.key: str = key
        self.value: str = value

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,  # pylint: disable=unused-argument
        now: DatetimeOrNone = None,  # pylint: disable=unused-argument
    ) -> bool:
        # Ignore stat_result, only use path and key/value
        try:
            with path.open("r", encoding="utf-8") as f:
                data: dict[str, str] = json.load(f)
            return data.get(self.key) == self.value
        except (IOError, PermissionError, json.JSONDecodeError):
            return False


@pytest.mark.parametrize(
    "json_content, key, value, expected_result",
    [
        (
            {"Error": "File does not exist"},
            "Error",
            "File does not exist",
            True,
        ),  # pass match
        (
            {"Error": "Something else"},
            "Error",
            "File does not exist",
            False,
        ),  # fail match different
        (None, "Error", "File does not exist", False),  # fail file not found
    ],
)
def test_json_key_value_filter_param(
    tmp_path: pathlib.Path,
    json_content: str | None,
    key: str,
    value: str,
    expected_result: bool,
):
    # Arrange
    p = tmp_path / "sample.json"
    if json_content is not None:
        p.write_text(json.dumps(json_content))
    else:
        # Do not create the file for file not found case
        p = tmp_path / "nonexistent.json"

    # Act
    f = JsonKeyValueFilter(key, value)
    actual_result = f.match(p)

    # Assert
    assert actual_result is expected_result
