
# PathQL: Declarative Filesystem Query Language for Python

PathQL is a declarative, composable, and efficient query language for filesystem operations in Python. It enables expressive, readable, and powerful queries over files and directories, inspired by `pathlib` and modern query languages. PathQL is designed for performance (stat caching), extensibility, and testability, with robust operator overloading and a familiar, Pythonic API.

## Features
- **Declarative Query Syntax**: Compose filters using Python operators (`&`, `|`, `~`, etc.)
- **Pathlib-like Naming**: Filters and queries mimic `pathlib` conventions (e.g., `Stem`, `Suffix`, `Type`)
- **Stat Caching**: Each file is stat-ed only once per query for efficiency
- **Short-circuiting Boolean Logic**: AND/OR/NOT combinators short-circuit as expected
- **Extensible Filters**: Easily add new filters for custom logic
- **Comprehensive Testing**: Robust, parameterized pytest suite with coverage

## Installation

PathQL is a pure Python package. To use in your project:

```powershell
pip install -e .
```

Or simply copy the `src/pathql` directory into your project.

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

## Advanced Features

- **Stat Caching**: Each file is stat-ed once, and the result is passed to all filters, avoiding redundant system calls.
- **Short-circuiting**: Boolean combinators (`&`, `|`, `~`) short-circuit as in native Python logic.
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
