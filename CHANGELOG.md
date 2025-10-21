# Changelog

## [0.2.0] - 2025-10-20
### Added
- File filter uses shell-style globbing (fnmatch) for full filename matching.
- Suffix filter supports dot-prefixed, fnmatch-compatible patterns and wildcards.
- All filters and tests are PEP8 and docstring compliant.
- Improved documentation and test coverage.

### Changed
- File filter no longer supports curly-brace expansion (e.g., foo.{jpg,png}).
- Suffix filter matches using normalized dot-prefixed patterns and supports wildcards.
- All datetime usage is via `import datetime as dt` per project convention.

### Fixed
- Various test and documentation updates for new filter semantics.

---
