"""PathQL CLI entry point and minimal command-line interface."""

import argparse
import pathlib

from pathql import File, Query, __version__


def main():
    """Run the CLI to query files and print matches."""
    parser = argparse.ArgumentParser(
        description="PathQL: Declarative Filesystem Query Language",
        epilog="""
Examples:
  python -m pathql '*.py' --recursive
  python -m pathql 'foo*'

This will print all files matching the given stem pattern in the current directory.

Use --recursive to search subdirectories.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "pattern",
        type=str,
        help="File stem pattern (e.g. 'foo*' or '*.txt'). Uses shell-style wildcards.",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Search directories recursively."
    )
    args = parser.parse_args()

    query = Query(File(args.pattern))
    print("PathQL v" + __version__)
    for f in query.files(path=pathlib.Path("."), recursive=args.recursive, files=True):
        print(f)


if __name__ == "__main__":
    main()
