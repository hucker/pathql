
![pytest](https://img.shields.io/badge/pytest-530-brightgreen) ![ruff](https://img.shields.io/badge/ruff-passed-brightgreen) ![Python 3.10–3.14](https://img.shields.io/badge/python-3.10--3.14-blue.svg)


## PathQL: Declarative Filesystem Query Language for Python

PathQL is a declarative, composable, and efficient query language for filesystem operations in Python. It enables expressive, readable, and powerful queries over files and directories, inspired by `pathlib` and modern query languages. PathQL is designed for performance (stat caching), extensibility, and testability, with robust operator overloading and a familiar, Pythonic API requiring no (or VERY few) interactions and conversions with `datetimes`, `timestaps` and vaguaries of the `os.stat_result` object.

## Features

- **Declarative Query Syntax**: Compose filters using Python operators (`&`, `|`, `~`, etc.)
- **Pathlib-like Naming**: Filters and queries mimic `pathlib` conventions (e.g., `Stem`, `Suffix`, `FileType`)
- **Stat Caching**: Each file is stat-ed at-most, once, even if there are many checks against "stat-able" parts of a file.
- **Threaded Filesystem Search**: Query engine uses a producer-consumer model with a dedicated thread for filesystem crawling and a main thread for filtering, improving responsiveness and throughput for large directory trees.
- **Extensible Filters**: Easily add new filters for custom logic
- **Comprehensive Testing**: Robust, parameterized pytest suite with coverage

## Basic Concepts

PathQL lets you write queries against the file system in a composable form:

```python
from pathql import AgeYears, Suffix, Query
for f in Query(where_expr=(AgeYears() > 1) & Suffix(".bak"), from_paths="c:/logs").files():
    print(f"Files to delete - {f.resolve()}")
```

```python
from pathql import AgeDays, Size, FileType, Suffix, Query
for f in Query(where_expr=(AgeDays() == 0) & (Size() > "10 mb") & Suffix("log"), from_paths="C:/logs", threaded=True).files():
    print(f"Files to zip - {f.resolve()}")
```

```python
from pathql import AgeDays, Size, Suffix, Query,ResultField

# Count, largest file size, and oldest file in the result set
query = Query(
    where_expr=(AgeDays() == 0) & (Size() > "10 mb") & Suffix("log"),
    from_paths="C:/logs",
    threaded=True
)
result_set = query.select()

print(f"Number of files to zip: {result_set.count_()}")
print(f"Largest file size: {result_set.max(ResultField.SIZE)} bytes")
print(f"Oldest file: {result_set.min(ResultField.MTIME)}")
```

These examples show how `PathQL` hides the guts of the pathlib module and the os module from you with readable filter expressions.  The real power comes with actions that allow you to apply a function to all of the files that match your query, in parallel.



### Composition and Filters

Filters are composable objects that match files based on many of the attributes exposed by the `pathlib` Package. Attributes such as size, age, suffix, stem, or type. Each filter can be combined using Python's over-loadable boolean operators. Those filters can be composed in arbitrarily complex ways using boolean operators and methods that operate on queries.

# Boolean Filter Functions(all/any) and Operators: `&`, `|`, `~`

PathQL allows you to compose complex queries using the `&` (AND), `|` (OR), and `~` (NOT) operators. These operators work analogously to Python's built-in `and`, `or`, and `not`, but are implemented using operator overloading to allow chaining and composition of filter objects.

- `&` (AND): Combines two filters so that both must match for a file to be included.
- `|` (OR): Combines two filters so that either filter matching will include the file.
- `~` (NOT): Inverts the result of a filter, matching files that do **not** satisfy the filter.
- **Any(q1,q2,..)** and **All(q1,q2,...** composable queries allow for short circuited sub query composition.

**Precedence**

The query language implemented by `PathQL` should be thought of as a mathematical system that uses pythons mathematical operators, as such the rules of precedence follow those for '&', `|` and `^`, which have different precedence than the `and`/`or` operators (which cannot be overloaded).

You must say

`(AgeDays() < 2) & (Suffix("txt))`

for precedence to work as you expect, or use the `All`/`Any` methods.

**Short-Circuiting Behavior**

PathQL's filter composition is designed to short-circuit, just like Python's boolean operators:

- For `A & B`, if filter `A` does not match, filter `B` is **not** evaluated.
- For `A | B`, if filter `A` matches, filter `B` is **not** evaluated.
- For chained filters (e.g., `A & B & C`), evaluation stops at the first filter that fails for AND, or the first that succeeds for OR.
- For `All(A,B,C)` or `Any(A,B,C)`, the operation will short circuit once a `All` sees a `False` or `Any` sees a `True`.

Place expensive filters at right most position in expressions so they can be short circuited.

**Example 1**

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
combined = FalseFilter() & ExpensiveFilter()
result = combined.match(pathlib.Path("somefile.txt"))  # Fast, no delay

# ExpensiveFilter will NOT be called because CheapFilter succeeds
combined = TrueFilter() | ExpensiveFilter()
result = combined.match(pathlib.Path("somefile.txt"))  # Fast, no delay
```

**Example 2**
```python
# ExpensiveFilter will NOT be called because CheapFilter fails.  All Function mimics 'and'
combined = All(FalseFilter(), ExpensiveFilter())
result = combined.match(pathlib.Path("somefile.txt"))  # Fast, no delay

# ExpensiveFilter will NOT be called because CheapFilter succeeds.  Any function mimics 'or'
combined = Any(TrueFilter(), ExpensiveFilter())
result = combined.match(pathlib.Path("somefile.txt"))  # Fast, no delay
```

**Note:**
Filters should be pure functions without side effects, as short-circuiting means some filters may not be executed depending on the logic. While most filters that come with `pathql` run fairly quickly, real world use cases involve opening files and scanning contents for state information. Eliminating these checks can be VERY valuable.

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

The `Between` filter matches files whose attribute (such as size or age) falls within a specified range: inclusive on the lower bound, exclusive on the upper bound. This filter works with values that can be reduced to comparable values.  At this time `Size` and `FileDate` work with between.

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

The `Query` class is the driver for PathQL. It walks the filesystem, gathers stat metadata, and applies filter expressions to decide which files to yield. It exposes a small API and supports both single-threaded and producer/consumer (threaded) modes for flexible performance characteristics.

### Overview

- Purpose: efficiently find filesystem entries that match a filter expression. - Model: the filesystem walk (producer) is separated from filtering/consumption (consumer) so IO-bound directory traversal can proceed concurrently with CPU bound filter evaluation.
- Key features: stat caching, optional threading, recursion control, and
  eager or lazy collection via `select` and `files` respectively.

### Public API

- `Query(filter_expr)` — construct a Query with a filter expression (any `Filter`).
- `Query.match(path, now=None, stat_result=None)` — run the filter expression against a single `path`. Useful for programmatic checks or tests. `now` defaults to the current datetime `stat_result` can be provided to avoid an additional `stat()` call.
- `Query.files(path, recursive=True, files_only=True, now=None, threaded=False)` — lazily yield matching `pathlib.Path` objects. Set `threaded=True` to enable  the producer/consumer mode.
- `Query.select(path, ...)` — eagerly collect matches into a `ResultSet`.

### Threaded vs single-threaded

With `pathql` you get threading basically for free.  Just ask for it when you run a query and your query will use 5 threads, though you have control over this.  For custom filters that are IO bound threading will help, if you are running a free-threaded version of python it will also help on compute bound problems.

- Single-threaded (`threaded=False`) walks the tree and filters each entry in a single loop. Simpler and predictable; good for small trees or when threading
  is not desired.
- Threaded (`threaded=True`) starts a producer thread that walks the filesystem and pushes `(path, stat_result)` tuples into a bounded `queue.Queue` (default maxsize: 10). The consumer (caller) reads from the queue and runs the filter expression. This can improve throughput when the filesystem is slow or when filter evaluation is relatively expensive.
- The producer places a `None` sentinel on the queue when traversal completes; the consumer stops after seeing the sentinel and joins the producer thread.

### Stat caching and `stat_result`

- The producer (threaded mode) or the single-threaded walker performs `path.stat()` once per file (at most) and passes the `stat_result` along with the path to the filters. Filters should accept and refer the provided `stat_result` to avoid extra system calls.
- `stat-result` is only generated when it is actually used and if other filter expressions require stat, they use a cached version.
- All filters in PathQL accept optional `now` and `stat_result` parameters so that a single `now` timestamp can be used for consistent comparisons and
  so callers can reuse stat results.

### Timing ###

IN large directory trees with 100's or 1000's of files the time changes between the beginning and end of a query, sometimes by many seconds or more.  This can lead to race conditions when ages are calculated. The design decision that was made is that at the start of a query the current time is read (or a user provided one is used) for all datetime calculations.  This is imperfect because there are many possible issues.  For example, a  file existed when you started the run but was deleted when you finished.  There are many ways that this problem could be solved with varying degrees of "quality".

### Recursion, files vs directories

- `recursive=True` (default) uses `rglob("*")` to walk the tree; set `recursive=False` to restrict to the top-level directory via `glob("*")`.
- `files_only=True` (default) filters out non-files; set `files=False` to include directories in the results.

## ResultSet and ResultField

PathQL’s `ResultSet` is a materialized list of `pathlib.Path` objects returned by `Query.select()`. It provides aggregation, sorting, and statistical methods for analyzing query results. You can use `ResultField` to specify which file attribute to operate on.

### ResultSet Operations

| Operation                 | Description                            |
| ------------------------- | -------------------------------------- |
| `count_()`                | Number of items in the result set      |
| `sort_(field, ascending)` | Sort by a field (ascending/descending) |
| `top_n(field, n)`         | Top N items by field                   |
| `bot_n(field, n)`         | Bottom N items by field                |
| `max(field)`              | Maximum value for a field              |
| `min(field)`              | Minimum value for a field              |
| `average(field)`          | Average value for a field              |
| `median(field)`           | Median value for a field               |

### ResultField Options

| Field                 | Description                        |
| --------------------- | ---------------------------------- |
| `SIZE`                | File size in bytes                 |
| `MTIME`               | Modification time (timestamp)      |
| `CTIME`               | Creation time (timestamp)          |
| `ATIME`               | Access time (timestamp)            |
| `MTIME_DT`            | Modification time (datetime)       |
| `CTIME_DT`            | Creation time (datetime)           |
| `ATIME_DT`            | Access time (datetime)             |
| `NAME`                | File name                          |
| `SUFFIX`              | File extension                     |
| `STEM`                | File stem (name without extension) |
| `PATH`                | Full path as string                |
| `PARENT`              | Parent directory                   |
| `PARENTS`             | All parent directories (tuple)     |
| `PARENTS_STEM_SUFFIX` | (Parents, stem, suffix) tuple      |

### Examples

```python
from pathql.query import Query
from pathql.result_fields import ResultField

# Get a result set of all .log files
result_set = Query(where_expr=Suffix(".log"), from_paths="./logs").select()

# Count files
print(result_set.count_())

# Get top 3 largest files
top_3 = result_set.top_n(ResultField.SIZE, 3)

# Sort by creation time (ascending)
sorted_by_ctime = result_set.sort_(ResultField.CTIME, ascending=True)

# Get file with latest modification time
latest = result_set.max(ResultField.MTIME)
```


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

The `Suffix` filter match file extensions by checking if the filename ends with the full extension, including the dot. Patterns like 'bmp' or '.bmp' are both accepted, but are normalized internally to '.bmp'.

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
".tif" and ".jpg" (you can also include a base, e.g. ".{tif,jpg}"). This is a convenience for common multi-extension cases. By contrast, the
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



### Custom Filter Classes

For more advanced logic, subclass `Filter` and implement the `match()` method. This gives you full control over how files are evaluated.

**Example: Custom Filter for minimum line count**
```python
from pathql.filters.base import Filter
from pathql.query import Query
from pathql.filters import Suffix

class MinLinesFilter(Filter):
    def __init__(self, min_lines: int):
        self.min_lines = min_lines

    def match(self, path: pathlib.Path, now=None, stat_result=None) -> bool:
        try:
            return sum(1 for _ in path.open()) >= self.min_lines
        except (IOError,PermissionError,FileNotFoundError):
            return False

# Place Suffix first for short-circuiting, then MinLinesFilter
for p in Query(where_expr=Suffix(".txt") & MinLinesFilter(100), from_paths="./docs"):
    print(p)
```

See `test/test_override.py` for more examples and patterns.

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


### Examples

| FilterName  | base_time                 | offset | attr  | Description                                                  |
| ----------- | ------------------------- | ------ | ----- | ------------------------------------------------------------ |
| HourFilter  | datetime(2022,10,28,11,0) | 2      | mtime | Files will match if modified in the hour 13:00 on 2022-10-28 |
| HourFilter  | None (current_time)       | 0      | ctime | Files will match if created in the current hour              |
| DayFilter   | datetime(2022,1,1)        | 0      | atime | Files will match if accessed on 2022-01-01                   |
| DayFilter   | None (current_time)       | -1     | mtime | Files will match if modified yesterday                       |
| MonthFilter | datetime(2023,6,1)        | -1     | ctime | Files will match if created in May 2023                      |
| MonthFilter | None (current_time)       | 0      | mtime | Files will match if modified this month                      |
| YearFilter  | datetime(2020,1,1)        | 1      | mtime | Files will match if modified in 2021                         |
| YearFilter  | None (current_time)       | 0      | ctime | Files will match if created this year                        |

**Example usage:**
```python
HourFilter(base_time=datetime(2022,10,28,11,0), offset=2, attr="mtime")
HourFilter(base_time=None, offset=0, attr="ctime")
DayFilter(base_time=datetime(2022,1,1), offset=0, attr="atime")
DayFilter(base_time=None, offset=-1, attr="mtime")
MonthFilter(base_time=datetime(2023,6,1), offset=-1, attr="ctime")
MonthFilter(base_time=None, offset=0, attr="mtime")
YearFilter(base_time=datetime(2020,1,1), offset=1, attr="mtime")
YearFilter(base_time=None, offset=0, attr="ctime")
```

## Age Filters

PathQL provides convenient age-based filters that match files based on their modification age. These are higher-level than the datetime-part filters and are useful for queries like "files older than 30 days" or "files modified in the last 2 hours".

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
for path in Query("/data", query).files():
    print(path)

# Files modified last month (-1 month  from this month)
query = MonthFilter(offset=-1)
for path in Query("/data" query).files():
    print(path)

# Files modified the day before Christmas 2023
christmas = dt.datetime(2022, 12, 25)
query = DayFilter(base=christmas, offset=-1)
for path in Query("/data", query).files():
    print(path)
```

Ideally, if you have a datetime value in your code you will never need to deal with time spans or deltas or complex data calculations.

## File Age Filters

PathQL supports filtering files by age using either filesystem timestamps or the date encoded in the filename. Using filename dating allows for a (possibly) more reliable way to target creation time in log files.  Instead of using the operating system timing data we use the file naming convention where the file name starts with YYYY-MM-DD-HH-, YYYY-MM-DD_, YY-MM_, YY_ Using this time can get around issues with creation tme not being reliable across operating systems, modification times being changed by mistake.  System clocks not be correct.

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

PathQL provides utilities for batch file operations on lists of `pathlib.Path` objects (or `ResultSet`). You can use a query to select files, then copy, move, delete or zip them:

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

## UV Example

### 1. Find all PNG or BMP images under 1MB, modified in the last 10 minutes

`PathQL` has a small CLI app called `pql.py1` that can be run from the command line using `uv`. It is a basic app that pulls in `pathql` and `PIL` and runs from the command line.  It has a custom filter object that looks into image file metadata and extracts the color depth allowing you filter files by color depth.  The demo enables color depth age and size filtering.



```bash
cli %  uv run --script pql.py "*.jpg" RGB
black_1kb.jpg

```

This command will:
- Build a virtual environment with python 3.14 and install pathql and PIL
- Search for files matching the pattern `*.jpg` in the current directory
- Filter for images with color mode `RGB`

You can add more options, such as file size and age:

```bash
cli % uv run --script pql.py "*.jpg" RGB --size-min 10kb --size-max 2mb --min-age 0 --max-age 365
```

This will:
- Build a virtual environment with python 3.14 and install pathql and PIL
- Find JPEG images with RGB color mode
- Only include files between 10KB and 2MB
- Only include files created between 0 and 365 days ago
- Return nothing because the file size constraint missed.

### Arguments

- **pattern** (positional): Glob pattern for files (e.g., `"*.jpg"`)
- **col_mode** (positional): Comma-separated color modes (e.g., `"RGB,RGBA,L"`)
- **--root**: Folder to search (default: current directory)
- **--size-min**: Minimum file size in bytes (default: 0)
- **--size-max**: Maximum file size in bytes (default: 1TB)
- **--min-age**: Minimum file creation age in days (default: 0)
- **--max-age**: Maximum file creation age in days (default: 100000)


## Note on Types: Operator Overloads in DSLs

PathQL filter classes (like `Size`, `AgeDays`, etc.) intentionally override Python's comparison and boolean operator methods (`__eq__`, `__lt__`, etc.) to return filter objects, not `bool`. This enables expressive, composable query logic:

```python
Size() > "10MB"   # returns a filter, not a bool
```

This pattern is common in query builders and DSLs, but it conflicts with Python's type system and expectations for these dunder methods (which are supposed to return `bool`). As a result, type checkers (like mypy, Pyright) and some linters will report errors or warnings about return types and operator overloads.

**Why?**
- Python expects `__eq__`, `__lt__`, etc. to return `bool` for built-in types.
- DSLs return filter objects so you can build up complex queries using operators.
- This is deliberate and necessary for PathQL's design, but it is not type-safe
    according to Python's current type system.

**What to do?**
- Ignore these type errors for filter classes, or use `# type: ignore` comments.
- Document this behavior for users and contributors.
- If you need strict `bool` results, use explicit methods or evaluate filters directly.

**Community Note:**
This is a known limitation in Python's type system. A future PEP may address DSL-friendly operator overloads, but for now, this pattern will always cause typechecker friction.

---
## Developer & Release Conventions

Project-level conventions, contributor guidance, and release steps are maintained in `AI_CONTEXT.md` in the repository root. Please consult that file for the latest instructions on coding style, testing, and release procedures.

---


## Release Summary

### Version: **v0.0.7** &nbsp;|&nbsp; Date: 2025-10-29

#### Highlights

- **README.md refactored:** Fixed issue in `README.md` file. Did not double check AI.
