# PathQL Declarative SQL Globbing

---

## Table of Contents
1. [Features](#features)
2. [Basic Concepts](#basic-concepts)
3. [Usage Examples](#usage-examples)
4. [Threading](#threading)
5. [Advanced Features](#advanced-features)
6. [Testing & Coverage](#testing--coverage)
7. [Extending PathQL](#extending-pathql)
8. [Project Structure](#project-structure)
10. [Date/Time Filtering Examples](#5-find-files-by-modification-or-creation-datetime)

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


#### Example Filters

- `Size() <= 1_000_000` — files up to 1MB
- `Suffix({".png", ".jpg"})` — files with .png or .jpg extension
- `Stem("report_*")` — files whose stem matches a glob pattern (e.g., starts with "report_")
- `Type("file")` — regular files
- `AgeMinutes < 10` — modified in the last 10 minutes
- `Between(Size(), 1000, 2000)` — files with size >= 1000 and < 2000 bytes (inclusive lower, exclusive upper)

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

A `Query` object recursively walks a directory and lazily yields files matching the filter expression, one at a time as they are found. Stat results are cached and passed to all filters for efficiency.

#### Threaded Producer-Consumer Model

PathQL's query engine uses a threaded producer-consumer model:

- A dedicated producer thread crawls the filesystem and enqueues file info.
- The main thread consumes from the queue, applies filters, and yields matches.
- The queue size is limited (default: 10) to balance memory and throughput.
This design improves responsiveness and performance, especially for large or slow filesystems.

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

## Threading


PathQL supports both threaded and non-threaded filesystem crawling:

- **Threaded crawling** (default) uses a producer-consumer model to overlap I/O operations, which can speed up queries on slow disks (HDDs).
- **Non-threaded crawling** processes files sequentially and may be just as fast or faster on modern SSDs, where disk access is already very fast.

Use `Query.files(...)` for threaded crawling (default), or `Query.unthreaded_files(...)` for non-threaded crawling.


## Advanced Features

- **Stat Caching**: Each file is stat-ed once, and the result is passed to all filters, avoiding redundant system calls.
- **Operator Overloading**: Filters can be combined at the class or instance level, e.g., `Size <= 1024` or `Suffix({".txt"}) | Suffix({".md"})`.
- **Pathlib-like Aliases**: Many filters have aliases for idiomatic usage (e.g., `Name = Stem`).

## Testing & Coverage

Run all tests with coverage:

```powershell
pytest --cov=src/pathql --cov-report=xml
```

Coverage results are saved to `coverage.xml`.

## Extending PathQL

To add a new filter:
1. Subclass `Filter` from `src/pathql/filters/base.py`.
2. Implement the `match(self, path, now=None, stat_result=None)` method.
3. Add operator overloading if needed (see existing filters for examples).
4. Add tests in `test/`.

## Project Structure

- `src/pathql/filters/`: Filter classes (Size, Suffix, Stem, Type, Age, etc.)
- `src/pathql/query.py`: Query class for recursive search
- `test/`: Pytest-based tests
- `pyproject.toml`: Project and coverage configuration


## Presets

PathQL provides convenient preset filters for common date-based queries. These presets simplify matching files by modification or creation time (e.g., today, this hour, this year).

### Available Presets

| Preset Function              | Description                       |
|------------------------------|-----------------------------------|
| `modified_this_minute`       | Files modified this minute         |
| `modified_this_hour`         | Files modified this hour           |
| `modified_today`             | Files modified today               |
| `modified_yesterday`         | Files modified yesterday           |
| `modified_this_month`        | Files modified this month          |
| `modified_this_year`         | Files modified this year           |
| `created_this_minute`        | Files created this minute          |
| `created_this_hour`          | Files created this hour            |
| `created_today`              | Files created today                |
| `created_yesterday`          | Files created yesterday            |
| `created_this_month`         | Files created this month           |
| `created_this_year`          | Files created this year            |

### Usage Example

```python
from pathql.presets.dates import modified_today
from pathql.query import Query

for path in Query("/some/dir", modified_today()):
   print(path)
```

---

For more examples and advanced usage, see the tests in `test/`.

### 5. Find files by modification or creation date/time

You can filter files by their modification or creation time using the `Modified` and `Created` filters, with expressive, compositional syntax:

#### Match files modified in 2025
```python
from pathql.filters.datetimes_ import Modified, Year
from pathql.query import Query

query = Modified(Year == 2025)
for path in Query("/data", query):
   print(path)
```

#### Match files created in January
```python
from pathql.filters.datetimes_ import Created, Month
from pathql.query import Query

query = Created(Month == 1)
for path in Query("/data", query):
   print(path)
```

#### Match files modified on a specific date
```python
import datetime
from pathql.filters.datetimes_ import Modified, Day
from pathql.query import Query

query = Modified(Day == datetime.date(2025, 10, 16))
for path in Query("/data", query):
   print(path)
```

#### Advanced: Use a custom extractor, operator, and value
```python
import operator
from pathql.filters.datetimes_ import Modified, Created

# Files modified in December
mod_dec = Modified(lambda dt: dt.month, operator.eq, 12)
# Files created in the first three hours of the day
created_early = Created(lambda dt: dt.hour, operator.in_, [0, 1, 2])
```

## CLI Usage

PathQL's CLI provides pattern-based file matching and recursive search, similar to an enhanced `ls` with globbing. It does not currently support interactive filter composition or a true REPL for advanced PathQL expressions.

### Basic Usage

Run PathQL from the command line to match files by pattern:

```bash
python -m pathql '*.py' -r
```

- The first argument is a glob pattern (e.g., `*.py`, `foo*`, `*.md`).
- Use the `-r` flag for recursive search in subdirectories.
- The CLI prints the package name and version before showing results.

Example output:
```
$ python -m pathql '*.py' -r
PathQL vX.Y.Z
main.py
query.py
filters/base.py
...
```

### Limitations
- The CLI does **not** provide a true interactive REPL for composing complex PathQL filter expressions.
- Only pattern matching and recursive search are supported from the command line.
- For advanced queries, use PathQL as a Python library in your own scripts.

## WARNING: Symlink and broken symlink handling is platform-dependent and not well tested across all OSes and edge cases. Results may vary depending on your operating system and filesystem. Use caution when relying on symlink detection in PathQL filters and queries.