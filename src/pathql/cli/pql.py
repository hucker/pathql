#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pathql"]
# ///

import argparse
import pathql
from typing import Optional

def main() -> None:
    parser = argparse.ArgumentParser(description="List files filtered by age, size, extension, name, and file dates.")
    parser.add_argument("--age-days", type=float, help="Match files older than this many days (float allowed)")
    parser.add_argument("--age-minutes", type=float, help="Match files older than this many minutes (float allowed)")
    parser.add_argument("--size-gt", type=str, help="Match files larger than this size (e.g. 2GB, 500K)")
    parser.add_argument("--size-lt", type=str, help="Match files smaller than this size (e.g. 2GB, 500K)")
    parser.add_argument("--ext", type=str, help="Match files with this extension (e.g. .txt, .jpg)")
    parser.add_argument("--name", type=str, help="Match files with this name (supports glob patterns, e.g. report_*)")
    parser.add_argument("--created-before", type=str, help="Match files created before this date (YYYY-MM-DD)")
    parser.add_argument("--modified-before", type=str, help="Match files modified before this date (YYYY-MM-DD)")
    parser.add_argument("--accessed-before", type=str, help="Match files accessed before this date (YYYY-MM-DD)")
    parser.add_argument("folder", nargs="?", default=".", help="Folder to search")
    args: argparse.Namespace = parser.parse_args()

    # Convert age to seconds
    age_seconds: Optional[float] = None
    if args.age_days is not None:
        age_seconds = args.age_days * 86400
    elif args.age_minutes is not None:
        age_seconds = args.age_minutes * 60

    # Build filter expression
    filter_expr: pathql.filters.base.Filter = pathql.filters.AllowAll()
    if age_seconds is not None:
        filter_expr &= pathql.filters.AgeSeconds() > age_seconds
    if args.size_gt is not None:
        filter_expr &= pathql.filters.Size() > args.size_gt
    if args.size_lt is not None:
        filter_expr &= pathql.filters.Size() < args.size_lt
    if args.ext is not None:
        filter_expr &= pathql.filters.Ext(args.ext)
    if args.name is not None:
        filter_expr &= pathql.filters.Name(args.name)
    if args.created_before is not None:
        filter_expr &= pathql.filters.FileDate("created") < args.created_before
    if args.modified_before is not None:
        filter_expr &= pathql.filters.FileDate("modified") < args.modified_before
    if args.accessed_before is not None:
        filter_expr &= pathql.filters.FileDate("accessed") < args.accessed_before

    # List files
    for path in pathql.Query(args.folder, filter_expr):
        print(path)

if __name__ == "__main__":
    main()