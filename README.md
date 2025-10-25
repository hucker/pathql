
<!-- Badges -->
![pytest](https://img.shields.io/badge/pytest-233-blue)
![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![mypy](https://img.shields.io/badge/mypy-13-orange)
![ruff](https://img.shields.io/badge/ruff-passed-brightgreen)

# PathQL: Declarative SQL Layer For Pathlib

PathQL allows you to query `pathlib.Path` objects using a declarative syntax reminiscent of SQL.

## Table of Contents
- [Quick Examples](#quick-examples)
- [Features](#features)
- [Concepts & Filters](#concepts--filters)
- [Boolean Operators & Short-Circuiting](#boolean-operators--short-circuiting)
- [Query Engine](#query-engine)
- [Filter Reference](#filter-reference)
- [Datetime & Age Filters](#datetime--age-filters)
- [Filename Builders](#filename-builders)
- [File Actions](#file-actions)
- [Usage Examples](#usage-examples)
- [Developer & Release Conventions](#developer--release-conventions)
- [Release Summary](#release-summary)

## Quick Examples

```python
from pathql import AgeYears, Ext, Query
for f in Query("c:/logs", (AgeYears() > 1) & Ext(".bak")):
    print(f"Files to delete - {f.resolve()}")
```

```python
from pathql import AgeDays, Size, FileType
for f in Query(r"C:/logs", (AgeDays() == 0) & (Size() > "10 mb") & Ext("log"), threaded=True):
    print(f"Files to zip - {f.resolve()}")
```

```python
from pathql import DayFilter
import datetime as dt
for f in Query(r"C:/logs", DayFilter(base=dt.datetime(year=2020, month=1, day=1))):
    print(f"Files to zip - {f.resolve()}")
```

## Features

- Declarative query syntax with Python operators (`&`, `|`, `~`)
- Pathlib-like naming and conventions
- Stat caching for efficient file metadata access
- Threaded and single-threaded search
- Extensible filters and comprehensive testing

## Concepts & Filters

Filters are composable objects that match files based on attributes like size, age, suffix, stem, or type. Combine filters using Python’s boolean operators.

### Filter Reference

- `Size() <= 1_000_000` — files up to 1MB
- `Suffix({".png", ".jpg"})` — files with .png or .jpg extension
- `Stem("report_*")` — files whose stem matches a glob pattern
- `FileType().file` — file, dir, link
- `AgeMinutes() < 10` — modified in the last 10 minutes
- `Between(Size(), 1000, 2000)` — size in range
- `YearFilter(2024)`, `MonthFilter("May")`, etc.

## Boolean Operators & Short-Circuiting

- `&` (AND): Both filters must match.
- `|` (OR): Either filter matches (short-circuits if first matches).
- `~` (NOT): Inverts the filter.

**Short-circuiting:**
For `A & B`, if `A` fails, `B` is not evaluated.
For `A | B`, if `A` matches, `B` is not evaluated.

**Precedence:**
Use parentheses for clarity: `(AgeDays() < 2) & Ext("txt")`


## Query Engine

- `Query(filter_expr)` — construct a query
- `Query.match(path, stat_proxy=None, now=None)` — check a single file
- `Query.files(path_or_paths, ...)` — lazily yield matches from a single folder or a list of folders
- `Query.select(path_or_paths, ...)` — collect matches eagerly from a single folder or a list of folders

Both `files` and `select` accept either a single path (str or Path) or a list of paths. This allows you to query multiple folders in one call:

```python
# Query a single folder
for f in Query(Suffix('.txt')).files('/data/folder1'):
    print(f)

# Query multiple folders
folders = ['/data/folder1', '/data/folder2', '/data/folder3']
for f in Query(Suffix('.txt')).files(folders):
    print(f)

# Collect all matches from multiple folders
result = Query(Suffix('.txt')).select(folders)
print(list(result))
```

Supports threaded and single-threaded modes, stat caching, recursion, and result collection.

## Datetime & Age Filters

- `YearFilter`, `MonthFilter`, `DayFilter`, etc. — match by parts of file timestamps
- `AgeMinutes`, `AgeHours`, `AgeDays`, `AgeYears` — match by file age

**Filename-based Age Filters:**
Match files by date encoded in filename (e.g., `YYYY-MM-DD_HH_{ArchiveName}.{EXT}`).

## Filename Builders

Utility functions for generating sortable filenames:

```python
from pathql.filters.date_filename import path_from_dt_ints, path_from_datetime

# Integer components
print(path_from_dt_ints("archive", "zip", year=2022))  # 2022-archive.zip
print(path_from_dt_ints("archive", "zip", year=2022, month=7))  # 2022-07_archive.zip
print(path_from_dt_ints("archive", "zip", year=2022, month=7, day=15))  # 2022-07-15_archive.zip
print(path_from_dt_ints("archive", "zip", year=2022, month=7, day=15, hour=13))  # 2022-07-15_13_archive.zip

# Datetime object
import datetime
dt = datetime.datetime(2022, 7, 15, 13)
print(path_from_datetime("archive", "zip", "year", dt))   # 2022-archive.zip
print(path_from_datetime("archive", "zip", "month", dt))  # 2022-07_archive.zip
print(path_from_datetime("archive", "zip", "day", dt))    # 2022-07-15_archive.zip
print(path_from_datetime("archive", "zip", "hour", dt))   # 2022-07-15_13_archive.zip
```

## File Actions

Batch file operations: `copy_files`, `move_files`, `delete_files`, `zip_files`, etc.
Robust exception handling and result reporting.

## Usage Examples

- Find PNG/BMP images under 1MB, modified in last 10 minutes
- Find files with stem starting with "report_"
- Find directories older than 1 year
- Custom filters with functions

## Developer & Release Conventions

See `AI_CONTEXT.md` for coding style, contributing, and release steps.

## Release Summary

### Highlights
- File filter uses shell-style globbing
- Suffix filter supports dot-prefixed patterns and wildcards
- Improved documentation and test coverage

### Breaking Changes
- File filter does not support curly-brace expansion
- Suffix filter matches using normalized dot-prefixed patterns

## PathQL: Declarative Filesystem Query Language for Python

PathQL is a declarative, composable, and efficient query language for filesystem operations in Python. It enables expressive, readable, and powerful queries over files and directories, inspired by `pathlib` and modern query languages. PathQL is designed for performance (stat caching), extensibility, and testability, with robust operator overloading and a familiar, Pythonic API.

## Features

- **Declarative Query Syntax**: Compose filters using Python operators (`&`, `|`, `~`, etc.)
- **Pathlib-like Naming**: Filters and queries mimic `pathlib` conventions (e.g., `Stem`, `Suffix`, `FileType`)
- **Stat Caching**: Each file is stat-ed at-most, once, even if there are many checks against "stat-able" parts of a file.
- **Threaded Filesystem Search**: Query engine uses a producer-consumer model with a dedicated thread for filesystem crawling and a main thread for filtering, improving responsiveness and throughput for large directory trees.
- **Extensible Filters**: Easily add new filters for custom logic
- **Comprehensive Testing**: Robust, parameterized pytest suite with coverage

## Basic Concepts

### Filters

Filters are composable objects that match files based on many of the attributes exposed by the `pathlib` Package. Attributes such as size, age, suffix, stem, or type. Each filter can be combined using Python's over-loadable boolean operators.

# Boolean Filter Operators: `&`, `|`, `~`

PathQL allows you to compose complex queries using the `&` (AND), `|` (OR), and `~` (NOT) operators. These operators work analogously to Python's built-in `and`, `or`, and `not`, but are implemented using operator overloading to allow chaining and composition of filter objects.

- `&` (AND): Combines two filters so that both must match for a file to be included.
- `|` (OR): Combines two filters so that either filter matching will include the file.
- `~` (NOT): Inverts the result of a filter, matching files that do **not** satisfy the filter.

**Precedence**

The query langage implimented by `PathQL` should be thought of as a mathematical system that uses pythons mathematical operators, as such the rules of precedance follow those for '&', `|` and `^`, which have different precedance than the `and`/`or` operators (which cannot be overloaded).

You must say

`(AgeDays() < 2) & (Ext("txt))`

To make the implement an symbolic & operation.

**Short-Circuiting Behavior**

PathQL's filter composition is designed to short-circuit, just like Python's boolean operators:

- For `A & B`, if filter `A` does not match, filter `B` is **not** evaluated.
- For `A | B`, if filter `A` matches, filter `B` is **not** evaluated.
- For chained filters (e.g., `A & B & C`), evaluation stops at the first filter that fails for AND, or the first that succeeds for OR.

This means that if you have expensive filters (such as those that read file contents or perform slow network operations), place them at the end of an and expression.

**Example:**

```python
from pathql.filters.base import Filter, AndFilter, OrFilter

class ExpensiveFilter(Filter):
    def match(self, path, now=None, stat_result=None):
        # Simulate a slow operation
        import time
        time.sleep(1)
        return True

class TrueFilter(Filter):
    def match(self, path, now=None, stat_result=None):
        return True

class FalseFilter(Filter):
    def match(self, path, now=None, stat_result=None):
        return False

# ExpensiveFilter will NOT be called because CheapFilter fails
combined = FalseFilter & ExpensiveFilter()
result = combined.match(pathlib.Path("somefile.txt"))  # Fast, no delay

# ExpensiveFilter will NOT be called because CheapFilter succeeds
combined = TrueFilter() | ExpensiveFilter()
result = combined.match(pathlib.Path("somefile.txt"))  # Fast, no delay
```

**Note:**
Filters should be pure functions without side effects, as short-circuiting means some filters may not be executed depending on the logic.
While most filters that come with `pathql` run fairly quickly, real world use cases involve opening files and scanning contents for
state information.  Eliminating these checks can be VERY valuable.

**Summary:**

- Use `&`, `|`, and `~` to build complex queries.
- Follow precedence rules (Size()>"1mb")
- Short-circuiting ensures efficient evaluation and skips unnecessary work.
- Place expensive filters down stream in your logic chains Fast=(Ext,Name,FileDate) slow = (Size,Type,Date,Age)

#### Example Filters

- `Size() <= 1_000_000` — files up to 1MB
- `Suffix({".png", ".jpg"})` — files with .png or .jpg extension
- `Stem("report_*")` — files whose stem matches a glob pattern (e.g., starts with "report_")
- `FileType().file` — 'file, 'dir', 'link'
- `AgeMinutes() < 10` — modified in the last 10 minutes
- `Between(Size(), 1000, 2000)` — files with size >= 1000 and < 2000 bytes (inclusive lower, exclusive upper)
- `YearFIlter(2024)`
- `MonthFIlter("May")`
- `DayFilter(23)`
- `HourFilter(12)`
- `MinuteFilter(59)`
- `SecondFilter(40)`
- `FileDate().modified > dt.datetime(2025,1,1)`

### Using the `Between` Filter

The `Between` filter matches files whose attribute (such as size or age) falls within a specified range: inclusive on the lower bound, exclusive on the upper bound.

**Example:** Find files with size >= 1KB and < 2KB:

```python
from pathql.filters import Between, Size
from pathql.query import Query

for path in Query("/some/dir", Between(Size(), 1000, 2000) & Between(FileDate(),dt.datetime(2024,1,1),dt.datetime(2024,2,1))):
   print(path)
else:
   print("No files were found")
```

## Query (engine)

The `Query` class is the driver for PathQL. It walks the filesystem, gathers stat metadata, and applies filter expressions to decide which files to yield.
It exposes a small API and supports both single-threaded and producer/consumer (threaded) modes for flexible performance characteristics.

### Overview

- Purpose: efficiently find filesystem entries that match a filter expression. - Model: the filesystem walk (producer) is separated from filtering/consumption (consumer) so IO-bound directory traversal can proceed concurrently with CPU bound filter evaluation.
- Key features: stat caching, optional threading, recursion control, and
  eager or lazy collection via `select` and `files` respectively.

### Public API

- `Query(filter_expr)` — construct a Query with a filter expression (any `Filter`).
- `Query.match(path, now=None, stat_result=None)` — run the filter expression against a single `path`. Useful for programmatic checks or tests. `now` defaults to the current datetime `stat_result` can be provided to avoid an additional `stat()` call.
- `Query.files(path, recursive=True, files=True, now=None, threaded=False)` — lazily yield matching `pathlib.Path` objects. Set `threaded=True` to enable  the producer/consumer mode.
- `Query.select(path, ...)` — eagerly collect matches into a `ResultSet`.

### Threaded vs single-threaded

- Single-threaded (`threaded=False`) walks the tree and filters each entry in a single loop. Simpler and predictable; good for small trees or when threading
  is not desired.
- Threaded (`threaded=True`) starts a daemon producer thread that walks the filesystem and pushes `(path, stat_result)` tuples into a bounded `queue.Queue` (default maxsize: 10). The consumer (caller) reads from the queue and runs the filter expression. This can improve throughput when the filesystem is slow or when filter evaluation is relatively expensive.
- The producer places a `None` sentinel on the queue when traversal completes; the consumer stops after seeing the sentinel and joins the producer thread.

### Stat caching and `stat_result`

- The producer (threaded mode) or the single-threaded walker performs `path.stat()` once per file and passes the `stat_result` along with the path to the filters. Filters should accept and refer the provided `stat_result` to avoid extra system calls.
- All filters in PathQL accept optional `now` and `stat_result` parameters so that a single `now` timestamp can be used for consistent comparisons and
  so callers can reuse stat results.

### Recursion, files vs directories

- `recursive=True` (default) uses `rglob("*")` to walk the tree; set `recursive=False` to restrict to the top-level directory via `glob("*")`.
- `files=True` (default) filters out non-files; set `files=False` to include directories in the results.

### Result collection

- `files(...)` is lazy and yields matches as they are found. Use this when you want streaming behavior or to process very large trees without building a large in-memory list.
- `select(...)` eagerly collects matches into a `ResultSet` (which wraps the iterator into a list-like object). Use `select` for aggregations or when an in-memory snapshot is required.

### Examples

```py
from pathql.query import Query
from pathql.filters import Suffix, AgeDays

# Lazy, single-threaded: iterate matches as they are found
q = Query(Suffix('.log') & (AgeDays() > 30))
for p in q.files(pathlib.Path('/var/log'), threaded=False):
    print(p)

# Eager, threaded: traversal runs in a background producer thread
for p in Query(Suffix('.txt')).files(pathlib.Path('/data'), threaded=True):
        process(p)

# Programmatic single-match check
q = Query(AgeDays > 7)
if q.match(pathlib.Path('notes.txt')):
    print('old')
```

### Edge cases and notes

- The default queue max size (10) is a tradeoff between memory and producer progress; tuning may help for very large or very slow filesystems.
- Filters should avoid calling `stat()` themselves when a cached`stat_result` is provided. (os.stat is expensive on network file systems)
- When using `now`, pass a fixed datetime in tests to make results deterministic.

If you need more control (parallel consumers, custom traversal ordering, or different queueing semantics) you can implement your own driver that reuses the filter primitives exposed by PathQL.

## File and Suffix Filter Semantics

### File Filter

The `File` filter matches the full filename using shell-style glob patterns (via `fnmatch`). This means you can use wildcards like `*`, `?`, and character sets, but **curly-brace expansion** (e.g., `foo.{jpg,png}`) is **not supported**. Matching is case-insensitive.

**Examples:**

```python
File("*.jpg")         # matches "photo.jpg", "archive.backup.jpg"
File("foo.*")         # matches "foo.jpg", "foo.png", "foo.bmp"
File("*.tar.gz")      # matches "archive.tar.gz", "foo.bar.tar.gz"
File("foo.*.back")    # matches "foo.tif.back", "foo.txt.back"
File("*report*")      # matches any file with "report" in the name
```

**Note:** Patterns like `foo.{jpg,png}` will NOT expand to match multiple extensions. Use wildcards or run multiple queries if you need to match several extensions.

### Suffix Filter

The `Suffix` and `Ext` filters match file extensions by checking if the filename ends with the full extension, including the dot. Patterns like 'bmp' or '.bmp' are both accepted, but are normalized internally to '.bmp'.

- Any leading dot in the extension pattern is added if missing, so 'bmp' and '.bmp' are treated identically.
- Matching is case-insensitive.
- The filter matches if the filename ends with the normalized pattern (e.g., '.bmp'), regardless of how many dots precede it.
- Wildcards (e.g., `*`, `?`) are supported in Suffix patterns via `fnmatch`.

**Examples:**

```python
Suffix(".jpg")         # matches "photo.jpg", "archive.backup.jpg"
Suffix("jpg")          # also matches "photo.jpg", "archive.backup.jpg"
Suffix(".tar.gz")      # matches "archive.tar.gz", "foo.bar.tar.gz"
Suffix(".tif.back")    # matches "image.tif.back", "foo.tif.back"
Suffix(".back")        # matches "foo.back", "image.tif.back", "foo.txt.back"
Suffix(".foo")         # matches "bar.foo", "baz.bar.foo"
Suffix("*.gz")         # matches any file ending in ".gz"
```

Note on curly-brace expansion: `Suffix` supports simple brace expansion inside a single string. For example, `Suffix("{tif,jpg}")` expands to the two patterns
`".tif"` and `".jpg"` (you can also include a base, e.g. `".{tif,jpg}"`). This is a convenience for common multi-extension cases. By contrast, the
`File` filter does NOT perform curly-brace expansion (it uses `fnmatch` on the entire filename) — use multiple `Suffix` filters or explicit patterns for complex filename matching.

Multi-part extensions like '.tar.gz' or '.tif.back' are supported and will match files ending with those exact strings. Wildcards are supported for flexible matching.

For more advanced extension filtering, you can combine `Suffix` with other filters:

```python
from pathql.query import Query
for path in Query("/photos", Suffix('.jpg') & CameraMakeFilter("Canon")):
    print(path)
```

Example: brace expansion with `Suffix`:

```python
# matches files ending with .tif or .jpg
for p in Query("/images", Suffix("{tif,jpg}")):
    print(p)
```

Example: simple content-based filter written as a function and wrapped with `PathCallback`:

```python
from pathql.filters import PathCallback

def contains_keyword(path: pathlib.Path, keyword: str) -> bool:
    """Return True if the file contains the given keyword (simple UTF-8 search)."""
    try:
        return keyword in path.read_text(encoding="utf-8")
    except Exception:
        return False

todo_filter = PathCallback(contains_keyword)("TODO")

for p in Query("/project", todo_filter & Suffix(".py")):
    print(p)
```

## Datetime Part Filters

PathQL provides powerful filters for matching files based on specific parts of their modification, creation, or access datetime. These filters allow precise queries for year, month, day, hour, minute, and second.

### Key Idea

You almost never need to interact with the raw `datetime` objects if you are dealing with time scales relative to today. The filter constructors and defaults are designed so that typical queries (by year, month, day, etc.) will just work. You specify the part you care about (e.g., `YearFilter(2025)`, `MonthFilter("may")`), and PathQL will filter data in that time period. If that time period is in the future (you ask for May and it is April)

### How `base`, `offset`, and `attr` Work

- **base**: The reference datetime for the filter. By default, this is the current date/time, but you can set it to any `datetime` object. This is useful for queries like "files from the same month last year" or "files from a specific day."
- **offset**: An integer that shifts the `base` by the specified number of years, months, days, etc., depending on the filter. For example, `offset=-1` with a `MonthFilter` and the default base will match last month.
- **attr**: Which file timestamp to use. Accepts user-friendly names (`"modified"`, `"created"`, `"accessed"`) or raw stat attribute names (`"st_mtime"`, etc.). This lets you filter by modification, creation, or access time as needed.

### Available Filters

- `YearFilter(year, base=None, offset=0, attr="modified")`
- `MonthFilter(month, base=None, offset=0, attr="created")`
- `DayFilter(day, base=None, offset=0, attr="accessed")`
- `HourFilter(hour, base=None, offset=0, attr="modified")`
- `MinuteFilter(minute, base=None, offset=0, attr="modified")`
- `SecondFilter(second, base=None, offset=0, attr="modified")`

### Arguments

- **value** (`int` or `str`): The part to match (e.g., year=2025, month="may" or 5, day=16, etc.)
- **base** (`datetime`, optional): Reference datetime for offset calculation. Defaults to now.
- **offset** (`int`, optional): Offset to apply to the base datetime (e.g., offset=1 for next year/month/day).
- **attr** (`str`, optional): Which stat attribute to use. Accepts "modified", "created", "accessed" or "st_mtime", "st_ctime", "st_atime".

### Matching Logic

- The filter extracts the relevant part(s) from the file's stat timestamp (using the specified attr).
- It compares the extracted part(s) to the filter's value(s).
- For `MonthFilter`, both string names ("may", "january") and integers (1-12) are supported.
- For `DayFilter`, `HourFilter`, `MinuteFilter`, `SecondFilter`, the filter matches only if all parts (year, month, day, etc.) match exactly.

### Stat Attribute Mapping

### Stat Attribute Mapping

| Friendly name | stat attribute | Description                                                       |
| ------------- | -------------- | ----------------------------------------------------------------- |
| modified       | `st_mtime`   | File modification time (most commonly used for age calculations)  |
| created       | `st_ctime`   | File creation time (platform-dependent: more reliable on Windows) |
| accessed      | `st_atime`   | Last access time                                                  |

You can also pass the raw stat attribute names (`"st_mtime"`, `"st_ctime"`, `"st_atime"`) to the datetime-part filters directly.

Examples:

```py
# Use friendly name (default)
YearFilter(2025, attr="modified")

# Use raw stat attribute name
YearFilter(2025, attr="st_mtime")

# Match by creation time explicitly (platform-dependent)
MonthFilter("may", attr="created")
```

## Age Filters

PathQL provides convenient age-based filters that match files based on their
modification age. These are higher-level than the datetime-part filters and are
useful for queries like "files older than 30 days" or "files modified in the
last 2 hours".

Supported filters:

- `AgeMinutes` — age in minutes
- `AgeHours` — age in hours
- `AgeDays` — age in days
- `AgeYears` — age in years

Comparison semantics:

- Only `<`, `<=`, `>`, and `>=` style comparisons are supported for age filters. The library treats `<` and `>` as inclusive (so they behave like  `<=` and `>=` respectively) for convenience. Equality (`==`) and inequality (`!=`) comparisons are intentionally unsupported and will raise `TypeError`.

Examples:

```py
from pathql import AgeDays, AgeHours, AgeYears,Query

# Files older than 30 days
for p in Query("/var/log", AgeDays() > 30):
    print(p)

# Files modified in the last 2 hours
for p in Query("/tmp", AgeHours() < 2):
    print(p)

# Files older than one year
for p in Query("/archive", AgeYears() >= 1):
    print(p)


```

Note: age filters use the file modification time (`st_mtime`) and accept an optional `now` parameter when used programmatically (useful for reproducible tests). They also accept an optional  `stat_result` to avoid extra `stat()` calls when you already have file metadata.

- "created"  → `st_ctime`
- "accessed" → `st_atime`
- You can also use the raw stat attribute names directly.

### Examples

```python
from pathql import YearFilter, MonthFilter, DayFilter, Query
import datetime as dt

# Files modified in 2025
query = YearFilter(2025)
for path in Query("/data", query):
    print(path)

# Files created in May
query = MonthFilter("may", attr="created")
for path in Query("/data", query):
    print(path)

# Files modified on October 16, 2025
query = DayFilter(base=dt.datetime(2025, 10, 16))
for path in Query("/data", query):
    print(path)
```

### More Examples: Yesterday, Last Month, and Relative Dates

```python
import datetime as dt
from pathql import DayFilter, MonthFilter,Query

# Files modified yesterday (-1day from now)
query = DayFilter(offset=-1)
for path in Query("/data", query):
    print(path)

# Files modified last month (-1 month  from this month)
query = MonthFilter(offset=-1)
for path in Query("/data", query):
    print(path)

# Files modified the day before Christmas 2023
christmas = dt.datetime(2022, 12, 25)
query = DayFilter(base=christmas, offset=-1)
for path in Query("/data", query):
    print(path)
```

Ideally, if you have a datetime value in your code you will never need to deal with time spans or deltas or complex data calculations.

## File Age Filters

PathQL supports filtering files by age using either filesystem timestamps or the date encoded in the filename. Using filename dating allows for a (possibly) more reliable way to target creation time in log files.  Instead of using the operating system timing data we use the file naming convention where the file name starts with YYYY-MM-DD-HH-, YYYY-MM-DD_, YY-MM_, YY_ Using this time can get around issues with creation tme not being reliable across operrating systems, modification times being changed by mistake.  System clocks not be correct.

For the purpose of matching if a valid file date is not found the match does not occur, it is not an error.

### Filename-based Age Filters

These filters use the date encoded in the filename (e.g. `YYYY-MM-DD_HH_{ArchiveName}.{EXT}`):

- `FilenameAgeMinutes`
- `FilenameAgeHours`
- `FilenameAgeDays`
- `FilenameAgeYears`

**Example usage:**

```python
from pathql.filters.fileage import FilenameAgeDays

# Find files whose filename date is less than 10 days old
filter = FilenameAgeDays(operator.lt, 10)
filter.match("2024-05-01_report.txt")
```

Filename-based filters allow you to query files based on their logical age, independent of filesystem metadata.

### File Actions

PathQL provides utilities for batch file operations on lists of `pathlib.Path` objects (or `ResultSet`). You can use a query to select files, then copy, move, or delete them:

```python
from pathql.actions import copy_files, move_files, delete_files
from pathql.query import Query
from pathql.filters import Suffix

# Select all .txt files recursively from 'src'
files = Query(Suffix() == "txt").select(src, recursive=True)
destination = Path("dst")

copy_files(files, destination)
move_files(files, destination)
delete_files(files)
```

### Exception Handling in File Actions

All file actions (`copy_files`, `move_files`, `delete_files`) in PathQL are designed for robust batch processing. When you perform an action on a list of files:

- **Exceptions are caught per file**: If an error occurs (such as `IOError`, `PermissionError`, `OSError`, `FileNotFoundError`, or `NotADirectoryError`), it is caught for that specific file.
- **Result reporting**: The return value is a `FileActionResult` object, which contains:
  - `success`: a list of files that were processed successfully.
  - `failed`: a list of files that failed to process.
  - `errors`: a dictionary mapping each failed file to the exception that was raised.
  - `status`: True if `failed` list is empty.
- **No silent failures**: By default, exceptions are caught and reported in the result object. If you set `ignore_access_exception=False`, the first exception encountered will be raised immediately.
- **Status property**: You can check `result.status` to see if all files were processed successfully (`True` if no failures).

**Example:**

```python
result = copy_files(files, destination)
if not result.status:
    print("Some files failed:")
    for path, exc in result.errors.items():
        print(f"{path}: {exc}")
```

This design ensures you always know which files succeeded, which failed, and why—making batch file operations safe and transparent.

> **Note:** If you perform a combined action (such as `zip_move_files`), the returned `FileActionResult` will reflect the status for both the zip and the move actions. The `success`, `failed`, and `errors` fields will include results from all underlying operations.

## Zip Actions

You can create zip archives from lists of files, with options to preserve directory structure and chain actions (zip+delete, zip+move, zip+copy):

```python
from pathql.actions import zip_files, zip_delete_files
from pathql.query import Query
from pathql.filters import Suffix

# Select all .txt files recursively from 'src'
files = Query(Suffix() == "txt").select(src, recursive=True)
root = Path("src")
target_zip = Path("archive.zip")

# Zip files to a target folder
zip_files(files, root, target_zip, preserve_dir_structure=True)

# Zip files to target folder and delete files left behind.
zip_delete_files(files, root, target_zip)
```

## Yet More Usage Examples

### 1. Find all PNG or BMP images under 1MB, modified in the last 10 minutes

```python
from pathql.filters import Suffix, Size, AgeMinutes
from pathql.query import Query

query = (Suffix({".png", ".bmp"}) & (Size() <= 1_000_000) & (AgeMinutes() < 10))
for path in Query("/some/dir", query):
   print(path)
```

### 2. Find all files with stem starting with "report_" (case-insensitive)

```python
from pathql.filters import Stem, FileType
from pathql.query import Query

query = Stem("report_*") & FileType("file")
for path in Query("/data/reports", query):
   print(path)
```

### 3. Find all directories older than 1 year

```python
from pathql.filters import FileType, AgeYears
from pathql.query import Query

query = FileType("dir") & (AgeYears() > 1)
for path in Query("/archive", query):
   print(path)
```

### 4. Customize with functions (recommended)

You can create new Filter classes by overriding `Filter`, or you can create filters from plain callables using `PathCallback` (for functions that only need the `path`) or `MatchCallback` (for functions that accept `path, now, stat_result`) (please use this to take advantage of stat caching).

These helpers perform constructor-time validation (so mistakes surface early)
and act as factories that let you bind arguments:

```py
from pathql PathCallback, MatchCallback
import pathlib

# Simple path-only callback (checks EXIF 'Make' tag)
def exif_mfr_is(path: pathlib.Path, mfr: str) -> bool:
    """Check that EXIF 'Make' contains the given manufacturer string."""
    try:
        from PIL import Image

        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return False
            # EXIF tag 271 is 'Make'
            return mfr.lower() in str(exif.get(271, "")).lower()
    except Exception:
        return False

# Wrap as a PathCallback (bind the manufacturer)
exif_factory = PathCallback(exif_mfr_is)
canon_filter = exif_factory("Canon")

for ifile in Query('./images',Suffix(".jpg") & canon_filter()):
    print(ifile)

```

Using functions is quick and readable for small custom checks. For more complex
stateful logic it's still fine to write a `Filter` subclass.

## Filename Builders

PathQL provides utility functions for generating standardized, sortable filenames with date/time prefixes.
These filenames are compatible with the `FileAge*` classes, which infer age from file names.

You can generate filenames in two ways:

1. **Using explicit integer date components:**
   Pass `year`, `month`, `day`, and `hour` as needed. The width is inferred from which components are provided.
2. **Using `&` `datetime` object:**
   Pass a `datetime` and specify the desired width (`"year"`, `"month"`, `"day"`, `"hour"`). All date components are taken from the `datetime`.

### Function Signatures and Formats

- `path_from_dt_ints(name, ext, year, month=None, day=None, hour=None)`
  Formats (based on provided components):

  - `year` only: `YYYY-{ArchiveName}.{EXT}`
  - `year`, `month`: `YYYY-MM_{ArchiveName}.{EXT}`
  - `year`, `month`, `day`: `YYYY-MM-DD_{ArchiveName}.{EXT}`
  - `year`, `month`, `day`, `hour`: `YYYY-MM-DD_HH_{ArchiveName}.{EXT}`
- `path_from_datetime(name, ext, width, dt)`
  Formats (based on `width`):

  - `"year"`: `YYYY-{ArchiveName}.{EXT}`
  - `"month"`: `YYYY-MM_{ArchiveName}.{EXT}`
  - `"day"`: `YYYY-MM-DD_{ArchiveName}.{EXT}`
  - `"hour"`: `YYYY-MM-DD_HH_{ArchiveName}.{EXT}`

### Usage Examples

```python
import datetime
from pathql.filters.date_filename import path_from_dt_ints, path_from_datetime

# Using explicit integer components
print(path_from_dt_ints("archive", "zip", year=2022))  # 2022-archive.zip
print(path_from_dt_ints("archive", "zip", year=2022, month=7))  # 2022-07_archive.zip
print(path_from_dt_ints("archive", "zip", year=2022, month=7, day=15))  # 2022-07-15_archive.zip
print(path_from_dt_ints("archive", "zip", year=2022, month=7, day=15, hour=13))  # 2022-07-15_13_archive.zip

# Using a datetime object and width
dt = datetime.datetime(2022, 7, 15, 13)
print(path_from_datetime("archive", "zip", "year", dt))   # 2022-archive.zip
print(path_from_datetime("archive", "zip", "month", dt))  # 2022-07_archive.zip
print(path_from_datetime("archive", "zip", "day", dt))    # 2022-07-15_archive.zip
print(path_from_datetime("archive", "zip", "hour", dt))   # 2022-07-15_13_archive.zip

```

**Note:**

- If `ext` is an empty string, no dot is added to the filename.
- If `.ext` is provided the `.` is removed internally, thus ".bmp" and "bmp" have the same effect.

## Developer & Release Conventions

Project-level conventions, contributor guidance, and release steps are maintained
in `AI_CONTEXT.md` in the repository root. Please consult that file for the
latest instructions on coding style, testing, and release procedures.

---

## Release Summary (v0.0.3, 2025-10-20)

### Highlights

- File filter now uses shell-style globbing (fnmatch) on full filenames.
- Suffix filter supports dot-prefixed, fnmatch-compatible patterns and wildcards.
- Curly-brace expansion is no longer supported in File filter.
- All filters and tests are PEP8 and docstring compliant.
- Improved documentation and test coverage.


