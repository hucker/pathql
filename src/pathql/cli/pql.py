#!/usr/bin/env -S uv run --script
# /// script
# python = "3.14"
# dependencies = ["pathql", "Pillow"]
# ///

import argparse
import pathlib

# These imports are not visible here because the code is a demo that
# will run under a script environment where pathql is installed.
# uv run --script pdl.py --
from PIL import Image  # noqa

import pathql
from pathql.filters.age import AgeDays
from pathql.filters.alias import DatetimeOrNone, StatProxyOrNone
from pathql.filters.base import Filter
from pathql.filters.size import Size


class ColorMode(Filter):
    """
    Filter for image color mode (e.g. 'RGB', 'RGBA', 'L', etc.).
    Accepts a comma-separated list of valid modes.
    """

    def __init__(self, valid_modes: str):
        self.valid_modes = [
            m.strip().lower() for m in valid_modes.split(",") if m.strip()
        ]

    def match(
        self,
        path: pathlib.Path,
        stat_proxy: StatProxyOrNone = None,
        now: DatetimeOrNone = None,
    ):
        try:
            with Image.open(path) as img:
                return img.mode.lower() in self.valid_modes
        except Exception:
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Find image files by color mode, file size, and creation age.",
        formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(
            prog, width=120
        ),
    )
    parser.add_argument(
        "pattern",
        nargs="?",
        help="Glob pattern for image files (default: *.jpg)",
    )
    parser.add_argument(
        "col_mode",
        help="Comma-separated list of valid color modes (e.g. RGB,RGBA,L) [required]",
    )
    parser.add_argument(
        "--root", default=".", help="Folder to search (default: current directory)"
    )
    parser.add_argument(
        "--size-min", default="0", help="Minimum file size in bytes (default: 0)"
    )
    parser.add_argument(
        "--size-max", default="10Gb", help="Maximum file size in bytes (default: 10Gb)"
    )
    parser.add_argument(
        "--min-age",
        type=int,
        default=0,
        help="Minimum file creation age in days (default: 0)",
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=100000,
        help="Maximum file creation age in days (default: 100000)",
    )
    args = parser.parse_args()

    # Build filter expression
    filter_expr = pathql.filters.File(args.pattern)
    color_modes = [m.strip().upper() for m in args.col_mode.split(",") if m.strip()]
    color_filter = None
    for m in color_modes:
        f = ColorMode(m)
        color_filter = f if color_filter is None else (color_filter | f)
    filter_expr &= color_filter
    filter_expr &= Size() >= args.size_min
    filter_expr &= Size() <= args.size_max
    filter_expr &= AgeDays() >= args.min_age
    filter_expr &= AgeDays() <= args.max_age

    for path in pathql.Query(filter_expr).files(args.root):
        print(path)


if __name__ == "__main__":
    main()
