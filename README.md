
<!-- Badges: pytest count, coverage (src), mypy errors, ruff status -->

![pytest](https://img.shields.io/badge/pytest-233-blue)
![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![mypy](https://img.shields.io/badge/mypy-13-orange)
![ruff](https://img.shields.io/badge/ruff-passed-brightgreen)

# PathQL Declarative SQL Globbing

---


## Quick Examples

Print backup files older than 1 year:

```py
from pathql import AgeYears, EXT

for f in Query("C:/logs",  (AgeYears > 1) & Ext(".bak")):
    print(f"Files to delete - {f.resolve()}")
```

Print files created today and larger than 10MB in C:\\logs:

```py
from pathql import AgeDays, Size, Type


for p in Query(r"C:/logs", (AgeDays == 0) & (Size() > "10 mb"):
    print(f"Files to zip - {f.resolve()}")
```



## Table of Contents
- [PathQL Declarative SQL Globbing](#pathql-declarative-sql-globbing)
  - [Quick Examples](#quick-examples)
  - [Table of Contents](#table-of-contents)
  - [PathQL: Declarative Filesystem Query Language for Python](#pathql-declarative-filesystem-query-language-for-python)
  - [Features](#features)
  - [Basic Concepts](#basic-concepts)
    - [Filters](#filters)
      - [Example Filters](#example-filters)
    - [Using the `Between` Filter](#using-the-between-filter)
    - [Query](#query)
      - [Threaded Producer-Consumer Model](#threaded-producer-consumer-model)
  - [File and Suffix Filter Semantics](#file-and-suffix-filter-semantics)
    - [File Filter](#file-filter)
    - [Suffix Filter](#suffix-filter)
  - [Datetime Part Filters](#datetime-part-filters)
    - [Key Idea](#key-idea)
    - [How `base`, `offset`, and `attr` Work](#how-base-offset-and-attr-work)
    - [Available Filters](#available-filters)
    - [Arguments](#arguments)
    - [Matching Logic](#matching-logic)
    - [Stat Attribute Mapping](#stat-attribute-mapping)
    - [Examples](#examples)
    - [More Examples: Yesterday, Last Month, and Relative Dates](#more-examples-yesterday-last-month-and-relative-dates)
  - [Usage Examples](#usage-examples)
    - [1. Find all PNG or BMP images under 1MB, modified in the last 10 minutes](#1-find-all-png-or-bmp-images-under-1mb-modified-in-the-last-10-minutes)
    - [2. Find all files with stem starting with "report\_" (case-insensitive)](#2-find-all-files-with-stem-starting-with-report_-case-insensitive)
    - [3. Find all directories older than 1 year](#3-find-all-directories-older-than-1-year)
    - [4. Use with custom filters](#4-use-with-custom-filters)
    - [5. Advanced Example: Custom Filter Using PIL for Image Metadata](#5-advanced-example-custom-filter-using-pil-for-image-metadata)
  - [Developer \& Release Conventions](#developer--release-conventions)
  - [Release Summary (v0.0.3, 2025-10-20)](#release-summary-v003-2025-10-20)
    - [Highlights](#highlights)
    - [Breaking Changes](#breaking-changes)
    - [Test Results](#test-results)
    - [Static Analysis](#static-analysis)

## PathQL: Declarative Filesystem Query Language for Python

PathQL is a declarative, composable, and efficient query language for filesystem operations in Python. It enables expressive, readable, and powerful queries over files and directories, inspired by `pathlib` and modern query languages. PathQL is designed for performance (stat caching), extensibility, and testability, with robust operator overloading and a familiar, Pythonic API.

## Features

- **Declarative Query Syntax**: Compose filters using Python operators (`&`, `|`, `~`, etc.)
- **Pathlib-like Naming**: Filters and queries mimic `pathlib` conventions (e.g., `Stem`, `Suffix`, `Type`)
- **Stat Caching**: Each file is stat-ed only once per query for efficiency
- **Threaded Filesystem Search**: Query engine uses a producer-consumer model with a dedicated thread for filesystem crawling and a main thread for filtering, improving responsiveness and throughput for large directory trees.
- **Extensible Filters**: Easily add new filters for custom logic
- **Comprehensive Testing**: Robust, parameterized pytest suite with coverage



## Basic Concepts

### Filters

Filters are composable objects that match files based on attributes such as size, age, suffix, stem, or type. Each filter can be combined using boolean operators:

**Note on Age Filters:**
Age filters (`AgeDays`, `AgeYears`, `AgeHours`, `AgeMinutes`) only support `>=` and `<=` comparisons. The `<` and `>` operators are treated as inclusive (`<=` and `>=`).
Equality (`==`) and inequality (`!=`) comparisons are not supported and will raise an error.

- `&` (AND)
- `|` (OR)
- `~` (NOT)

If you are familiar with `pandas` you will notice that instead of using python `and` `or` and `not` operators we use the ones shown above in order to build
up arbitrary boolean expressions in code.  This is actually a limitation of `python` (or a reach on my part to make this work).  Operators that short circuit do
not have dunder methods and can not be "overridden" from code so we are stuck using the mathematical equivalent operators.

#### Example Filters

- `Size() <= 1_000_000` — files up to 1MB
- `Suffix({".png", ".jpg"})` — files with .png or .jpg extension
- `Stem("report_*")` — files whose stem matches a glob pattern (e.g., starts with "report_")
- `Type("file")` — 'file, 'dir', 'link'
- `AgeMinutes < 10` — modified in the last 10 minutes
- `Between(Size(), 1000, 2000)` — files with size >= 1000 and < 2000 bytes (inclusive lower, exclusive upper)
- `YearFIlter(2024)`
- `MonthFIlter("May")`
- `DayFilter(23)`
- `HourFIlter(12)`
- `MinutFilter(59)`
- `SecondFilter(40`)

### Using the `Between` Filter


The `Between` filter matches files whose attribute (such as size or age) falls within a specified range: inclusive on the lower bound, exclusive on the upper bound.

**Example:** Find files with size >= 1KB and < 2KB:

```python
from pathql.filters import Between, Size
from pathql.query import Query

for path in Query("/some/dir", Between(Size(), 1000, 2000)):
   print(path)
else:
   print("No files were found")
```

### Query

A `Query` object recursively walks a directory and lazily yields files matching the filter expression, one at a time as they are found. Stat results are cached and
passed to all filters for efficiency. Care is taken to make all times relative to a fixed timestamp so all time calculations are consistent.  You could imagine for
very large folders that your runs could span various time boundaries if you always used the current time for comparisons.

#### Threaded Producer-Consumer Model

PathQL's query engine uses a threaded producer-consumer model:

- A dedicated producer thread crawls the filesystem and enqueues file info.
- The main thread consumes from the queue, applies filters, and yields matches.
- The queue size is limited (default: 10) to balance memory and throughput.
This design improves responsiveness and performance, especially for large or slow filesystems.

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

Multi-part extensions like '.tar.gz' or '.tif.back' are supported and will match files ending with those exact strings. Wildcards are supported for flexible matching.

For more advanced extension filtering, you can combine `Suffix` with other filters:
```python
from pathql.query import Query
for path in Query("/photos", Suffix('.jpg') & CameraMakeFilter("Canon")):
    print(path)
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
- "modified" → `st_mtime`
- "created"  → `st_ctime`
- "accessed" → `st_atime`
- You can also use the raw stat attribute names directly.

### Examples
```python
from pathql.filters.datetime_parts import YearFilter, MonthFilter, DayFilter
from pathql.query import Query
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
from pathql.filters.datetime_parts import DayFilter, MonthFilter
from pathql.query import Query

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

---

## Usage Examples

### 1. Find all PNG or BMP images under 1MB, modified in the last 10 minutes

```python
from pathql.filters import Suffix, Size, AgeMinutes
from pathql.query import Query

query = (Suffix({".png", ".bmp"}) & (Size() <= 1_000_000) & (AgeMinutes < 10))
for path in Query("/some/dir", query):
   print(path)
```

### 2. Find all files with stem starting with "report_" (case-insensitive)

```python
from pathql.filters import Stem, Type
from pathql.query import Query

query = Stem("report_*") & Type("file")
for path in Query("/data/reports", query):
   print(path)
```

### 3. Find all directories older than 1 year

```python
from pathql.filters import Type, AgeYears
from pathql.query import Query

query = Type("dir") & (AgeYears > 1)
for path in Query("/archive", query):
   print(path)
```

### 4. Use with custom filters

You can define your own filters by subclassing `Filter`:
```python
from pathql.filters.base import Filter

class Owner(Filter):
   def __init__(self, username):
      self.username = username
   def match(self, path, now=None, stat_result=None):
      return path.owner() == self.username
```

Then use it in a query:
```python
from pathql.query import Query
query = Owner("alice") & Type("file")
for path in Query("/home/alice", query):
   print(path)
```

### 5. Advanced Example: Custom Filter Using PIL for Image Metadata

You can create custom filters that use external libraries to inspect file contents or metadata. For example, to filter images by camera make using the Pillow (PIL) library:

```python
from pathql.filters import Filter
from PIL import Image
import pathlib

class CameraMakeFilter(Filter):
    """Filter images by EXIF camera make."""
    def __init__(self, make: str):
        self.make = make.lower()
    def match(self, path: pathlib.Path, **kwargs) -> bool:
        try:
            with Image.open(path) as img:
                exif = img.getexif()
                if not exif:
                    return False
                # EXIF tag 271 is 'Make' (camera manufacturer)
                camera_make = exif.get(271, "").lower()
                return self.make in camera_make
        except Exception:
            return False

# Usage: Find all JPEGs in /photos taken with a Canon camera
from pathql.query import Query


for path in Query("/photos", Suffix('jpg') & CameraMakeFilter("Canon")):
    print(path)
```


## Developer & Release Conventions

These project conventions are required for releases and developer contributions.

- Always import the stdlib datetime module with the `dt` alias:

```py
import datetime as dt
```

- Never use `datetime` as a variable or argument name. Use `dt`prefix for types
    (e.g. `dt.datetime`, `dt.date`, `dt.timedelta`).

- Prefer `import pathlib` and use `pathlib.Path` instead of importing path classes.

- Docstrings: keep function and method docstrings short (1-2 lines, <=88 chars).

- Function signatures with more than two parameters should put one parameter
    per line to avoid long lines and improve readability.

- Tests must follow Arrange–Act–Assert (AAA). Use short docstrings for tests and
    explicit `# Arrange`, `# Act`, `# Assert` comments inside the test body.

- Avoid curly-brace expansion in filename patterns (File filter uses fnmatch).

Developer commands (run from repository root):

```bash
# Run tests with coverage for the src folder
pytest --cov=src --cov-report=term

# Run mypy type checks
mypy src/pathql

# Run ruff linter
ruff check src test
```

If mypy reports missing stubs for third-party libs, install recommended stubs:

```bash
python -m pip install types-python-dateutil
```

When preparing a release, bump `version` in `pyproject.toml`, update
`CHANGELOG.md`, and ensure tests and linters are clean before tagging.


---

## Release Summary (v0.0.3, 2025-10-20)

### Highlights
- File filter now uses shell-style globbing (fnmatch) on full filenames.
- Suffix filter supports dot-prefixed, fnmatch-compatible patterns and wildcards.
- Curly-brace expansion is no longer supported in File filter.
- All filters and tests are PEP8 and docstring compliant.
- Improved documentation and test coverage.

### Breaking Changes
- File filter does not support curly-brace expansion (e.g., foo.{jpg,png}). Use wildcards or multiple queries.
- Suffix filter matches using normalized dot-prefixed patterns and supports wildcards.
- All datetime usage is via `import datetime as dt` per project convention.

### Test Results
- All tests pass: 233/233
- Coverage: 100% of src/

### Static Analysis
- mypy: 13 errors (see details in repository run); run `mypy src/pathql` to reproduce
- ruff: no linting issues found

This approach works for any custom logic—just implement the `match` method. You can combine your custom filter with built-in filters using `&`, `|`, and `~` for powerful queries.

