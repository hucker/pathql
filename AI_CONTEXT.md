# AI Coding Context: datetime Import Convention

## Project-wide Convention

- Always import the standard library datetime module as:

  ```python
  import datetime as dt
  ```

- Always be PEP8 compliant (e.g., spaces not tabs, new line at end of file, first line has code etc)
- Never use `import datetime` without aliasing, and never use `datetime` as a variable or argument name.
- import pathlib instead of "from datetime import datetime"
- All references to datetime classes and functions (e.g., `datetime.datetime`, `datetime.date`, `datetime.timedelta`) should be updated to use the `dt` prefix (e.g., `dt.datetime`, `dt.date`, `dt.timedelta`).
- This convention applies to all source files, test files, and documentation code blocks.

## Doc Strings

- Please always create docstiings for all functions, methods, classes and files.
- Function docstrings can be short 1 or 2 line descriptions in tests.
- Docstrings should be no longer than 88 characters

## Readme Files

- when code variables, function names, constants are referenced in document text they should be in back ticks.

## Rationale

- Prevents accidental shadowing of the `datetime` module by variables or arguments named `datetime`.
- Improves code clarity and consistency across the codebase.
- Makes it easy to distinguish between the module and any local variables.

## Example

```python
import datetime as dt

dt1 = dt.datetime(2024, 12, 25, 10, 30)
dt2 = dt.datetime.now()
delta = dt2 - dt1
print(dt1.date())
```

## Testing

### Testing Conventions

PathQL follows the Arrange-Act-Assert (AAA) pattern for writing tests. This pattern ensures clarity and consistency in test structure. Each test is divided into three distinct sections:

1. **Arrange**: Set up the test data, environment, and dependencies. If Python fixtures are used, they should be documented here.
2. **Act**: Perform the action or behavior being tested.
3. **Assert**: Verify the outcome.

### Inline Example

For simple tests, the AAA pattern can be followed inline:

```python
from pathql.filters import Size
from pathql.query import Query

def test_size_filter():
    # Arrange
    query = Size() <= 1024

    # Act
    results = list(Query("/some/dir", query))

    # Assert
    assert all(path.stat().st_size <= 1024 for path in results), "Some files exceed 1KB"
```

### Example with Fixtures

When using fixtures, the Arrange section should document their purpose:

```python
import pytest
from pathql.filters import Suffix
from pathql.query import Query

@pytest.fixture
def test_directory(tmp_path):
    # Arrange: Create a temporary directory with test files
    (tmp_path / "file1.txt").write_text("content")
    (tmp_path / "file2.log").write_text("content")
    return tmp_path

def test_suffix_filter(test_directory):
    # Arrange
    query = Suffix({".txt"})
    expected_len = 1
    expected_file = "file1.txt"

    # Act
    results = list(Query(test_directory, query))
    actual_len = len(results)
    actual_name = results[0].name

    # Assert
    assert actual_len == expected_len, "Only one .txt file should match"
    assert actual_name == expected_file, "Matched file name is incorrect"
```



### Simple One-Liner Tests

In some cases, tests can be written as one-liners when the behavior being tested is simple and self-explanatory. These tests should still be clear and maintainable, even without the explicit AAA structure.

#### Example

```python
def test_suffix_one_liner():
    assert Suffix({".txt"}).match("example.txt"), "Suffix filter failed for .txt"
```

While one-liner tests are acceptable for straightforward cases, they should be used sparingly and only when the intent is immediately obvious. For more complex scenarios, prefer the full AAA structure.

### Example: Using `pytest.raises` with Arrange/Act/Assert

When testing that a function raises an exception, use `pytest.raises` to verify the exception type. Below is a simple example that demonstrates how to structure such a test using the Arrange/Act/Assert pattern.

#### Example Test: `test_divide_by_zero`

This test ensures that dividing by zero raises a `ValueError`.  One could argue that the example below is simple enough that you could just write the test
directly, however the structure where # Arrange does the setup and the context manager handles the Act and Assert is the common structure for exception
testing since there insert is implicit inside he `pytest.raises` context manager.

```python
import pytest

def divide(a, b):
    """Simple function to divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def test_divide_by_zero():
    """Test that dividing by zero raises a ValueError."""
    # Arrange
    numerator = 10
    denominator = 0

    # Act and Assert
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(numerator, denominator)


### Multiple Tests

It is possible that there might be more than one test case for a given test, representing differnt conditions.  In this
case it is ok to use nomenclature reflective of the condition.  In this case the answers for the assert are simple comments
so it we just use the constant.  If the expected value is a complex data structure or object it then create save these values
to variables rather than calculating them in line on the assert.

```python
def test_edge():

    # Arrange
    high_val = .0001
    on_val = 0
    low_val = -.0001

    # Act
    actual_high = function_with_edge(high_val)
    actual_on = function_with_edge(on_val)
    actual_low = function_with_edge(low_val)

    # Assert
    assert actual_high is False
    assert actual_on is True
    assert actual low is False
```

### Best Practices

- **Clarity**: Ensure each section is clearly marked and easy to identify.
- **Fixtures**: Use fixtures for reusable setup logic, and document their role in the Arrange section.
- **Assert Messages**: Include descriptive messages in assertions to aid debugging.
- **Docstrings**: Add a one-line docstring to each test function to describe its purpose.

## Migration Guidance

- When refactoring or adding new code, always use `import datetime as dt`.
- Update all existing code to use the `dt.` prefix for all datetime-related calls.
- If you see `import datetime` or `from datetime import ...`, refactor to the above convention unless there is a compelling reason not to.
-

---
This file is intended for both human and AI contributors to ensure a consistent and robust datetime import style throughout the project.