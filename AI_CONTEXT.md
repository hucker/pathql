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
- Function docstrings can be short 1 or 2 line descriptions.

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

## Migration Guidance

- When refactoring or adding new code, always use `import datetime as dt`.
- Update all existing code to use the `dt.` prefix for all datetime-related calls.
- If you see `import datetime` or `from datetime import ...`, refactor to the above convention unless there is a compelling reason not to.

---
This file is intended for both human and AI contributors to ensure a consistent and robust datetime import style throughout the project.