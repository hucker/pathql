import pathlib
import re
import fnmatch
from .base import Filter
from .stem import Stem
from .suffix import Suffix

class File(Filter):
    """
    Filter for matching a file's full name, with support for:
    - Exact match (case-insensitive)
    - Wildcards (fnmatch, e.g. '*.db')
    - Regex (pattern starts with ^ or ends with $)
    - {stem} and {ext} macros (e.g. '{stem}.db')
    - Delegation to Stem and Suffix filters for advanced logic

    Example usage:
        File("Thumbs.db")
        File("*.db")
        File("{stem}.db")
        File(r"^foo_\\d+\\.txt$")
    """
    def __init__(self, pattern, ignore_case=True):
        self.pattern = pattern
        self.ignore_case = ignore_case
        self._expr = self._parse_pattern(pattern, ignore_case)

    def _parse_pattern(self, pattern, ignore_case):
        # If the pattern is a plain file name (no wildcards, no regex, no macros), split at last dot
        if (
            isinstance(pattern, str)
            and '.' in pattern
            and not any(c in pattern for c in "*?[]{}$")
            and not pattern.startswith("^")
            and not pattern.endswith("$")
        ):
            stem, suffix = pattern.rsplit('.', 1)
            return Stem(stem, ignore_case=ignore_case) & Suffix(suffix)
        # Handle {stem}.{ext} and {stem} macros
        if "{stem}" in pattern or "{ext}" in pattern:
            regex = pattern.replace("{stem}", r"(?P<stem>.+)").replace("{ext}", r"(?P<ext>.+)")
            return File._regex_expr(regex, ignore_case)
        # Handle curly-brace extension sets: foo*.{bmp,jpg}
        import re as _re
        m = _re.match(r"^(.*)\.\{([^}]+)\}$", pattern)
        if m:
            stem_pat, ext_pat = m.group(1), m.group(2)
            ext_list = [e.strip() for e in ext_pat.split(",")]
            return Stem(stem_pat, ignore_case=ignore_case) & Suffix(ext_list)
        # Wildcard pattern: '*.ext' or '*'
        if any(c in pattern for c in "*?["):
            if pattern.startswith("*.") and pattern.count(".") == 1:
                ext = pattern[2:]
                return Suffix(ext)
            elif '.' in pattern:
                stem_pat, ext = pattern.split('.', 1)
                return Stem(stem_pat, ignore_case=ignore_case) & Suffix(ext)
            else:
                return Stem(pattern, ignore_case=ignore_case)
        # Regex pattern
        if pattern.startswith("^") or pattern.endswith("$"):
            return File._regex_expr(pattern, ignore_case)
        # Fallback: exact match
        return Stem(pattern, ignore_case=ignore_case)

    @staticmethod
    def _regex_expr(pattern, ignore_case):
        import re as _re
        flags = _re.IGNORECASE if ignore_case else 0
        regex = _re.compile(pattern, flags)
        class _RegexFilter(Filter):
            def match(self, path, now=None, stat_result=None):
                return regex.match(path.name) is not None
        return _RegexFilter()

    def match(self, path: 'pathlib.Path', now=None, stat_result=None):
        if isinstance(self._expr, tuple) and len(self._expr) == 2:
            return self._expr[0].match(path, now=now, stat_result=stat_result) and self._expr[1].match(path, now=now, stat_result=stat_result)
        return self._expr.match(path, now=now, stat_result=stat_result)

    def as_stem_and_suffix(self):
        # If the pattern is a plain file name (no wildcards, no regex, no macros), split at last dot
        if (
            isinstance(self.pattern, str)
            and '.' in self.pattern
            and not any(c in self.pattern for c in "*?[]{}$")
            and not self.pattern.startswith("^")
            and not self.pattern.endswith("$")
        ):
            stem, suffix = self.pattern.rsplit('.', 1)
            return (Stem(stem, ignore_case=self.ignore_case), Suffix(suffix))
        return None
