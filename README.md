# PathQL Declarative SQL Globbing

## WARNING: Symlink and broken symlink handling is platform-dependent and not well tested across all OSes and edge cases. Results may vary depending on your operating system and filesystem. Use caution when relying on symlink detection in PathQL filters and queries.

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
9. [License](#license)
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

- `&` (AND)
- `|` (OR)
- `~` (NOT)

#### Example Filters

- `Size <= 1_000_000` — files up to 1MB
- `Suffix({".png", ".jpg"})` — files with .png or .jpg extension
- `Stem("report_*")` — files whose stem matches a glob pattern (e.g., starts with "report_")
- `Type("file")` — regular files
- `AgeMinutes < 10` — modified in the last 10 minutes

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

query = (Suffix({".png", ".bmp"}) & (Size <= 1_000_000) & (AgeMinutes < 10))
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

PathQL supports both threaded and non-threaded filesystem crawling. Threaded crawling can provide performance gains on systems with slow disks (HDD), as it overlaps I/O operations. However, on modern hardware with SSDs, the overhead of thread management and task switching is often comparable to the cost of stat calls, so performance gains may be limited or even negative. For SSDs, non-threaded crawling may be just as fast or faster.

## Threaded and Non-Threaded Query Engines

PathQL provides both threaded and non-threaded (single-threaded) query engines for filesystem traversal and filtering. The threaded engine uses a producer-consumer model to parallelize file system stat calls and filtering, while the non-threaded engine processes files sequentially.

### Why Threading?

Threading is used to help isolate and potentially speed up the operating system stat calls (which are often the main bottleneck when querying large filesystems, especially on traditional spinning hard drives). By overlapping I/O-bound operations, the threaded engine can provide significant speedups when disk access is slow.

### SSD vs HDD Performance

On modern machines with SSDs, the cost of stat calls and file access is extremely low. In these environments, the overhead of threading (context switching, queueing, etc.) can actually make the threaded engine slightly slower than the non-threaded version. On older machines or systems with spinning hard drives (HDDs), the threaded engine can provide substantial performance improvements by overlapping slow I/O operations.

### Usage

- Use `Query.files(...)` for the threaded engine (default).
- Use `Query.unthreaded_files(...)` for the non-threaded, sequential engine.


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

## License
MIT License

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
