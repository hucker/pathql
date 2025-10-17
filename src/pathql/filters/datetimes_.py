
import datetime as dt
import pathlib
import operator
import os
from .base import Filter


# Top-level filter classes for exact datetime matches
class _DayFilter(Filter):
	"""Filter for exact year, month, and day match."""
	def __init__(self, other:Filter, attr: str = 'st_mtime'):
		self.other = other
		self.attr = attr

	def match(self, path:pathlib.Path, now:dt.datetime|None=None, stat_result:os.stat_result|None=None)->bool:
		if stat_result is None:
			stat_result = path.stat()
		ts = getattr(stat_result, self.attr)
		dt_obj = dt.datetime.fromtimestamp(ts)
		return (dt_obj.year == self.other.year and dt_obj.month == self.other.month and dt_obj.day == self.other.day)

class _HourFilter(Filter):
	"""Filter for exact year, month, day, and hour match."""
	def match(self, path:pathlib.Path, now:dt.datetime|None=None, stat_result:os.stat_result|None=None)->bool:

		self.other = other
		self.attr = attr

	def match(self, path:pathlib.Path, now:dt.datetime|None=None, stat_result:os.stat_result|None=None)->bool:

		if stat_result is None:
			stat_result = path.stat()
		ts = getattr(stat_result, self.attr)
		dt_obj = dt.datetime.fromtimestamp(ts)
		if isinstance(self.other, dt.datetime):
			return (dt_obj.year == self.other.year and dt_obj.month == self.other.month and dt_obj.day == self.other.day and dt_obj.hour == self.other.hour)
		else:
			return (dt_obj.year == self.other.year and dt_obj.month == self.other.month and dt_obj.day == self.other.day)

class _MinuteFilter(Filter):
	"""Filter for exact year, month, day, hour, and minute match."""
	def __init__(self, other):
		self.other = other

	def match(self, path:pathlib.Path, now:dt.datetime|None=None, stat_result:os.stat_result|None=None)->bool:

		if stat_result is None:
			stat_result = path.stat()
		ts = getattr(stat_result, 'st_mtime')
		dt_obj = dt.datetime.fromtimestamp(ts)
		if isinstance(self.other, dt.datetime):
			return (dt_obj.year == self.other.year and dt_obj.month == self.other.month and dt_obj.day == self.other.day and dt_obj.hour == self.other.hour and dt_obj.minute == self.other.minute)
		else:
			return (dt_obj.year == self.other.year and dt_obj.month == self.other.month and dt_obj.day == self.other.day)

class _SecondFilter(Filter):
	"""Filter for exact year, month, day, hour, minute, and second match."""
	def __init__(self, other):
		self.other = other
	def match(self, path, now=None, stat_result=None):
		if stat_result is None:
			stat_result = path.stat()
		ts = getattr(stat_result, 'st_mtime')
		dt_obj = dt.datetime.fromtimestamp(ts)
		if isinstance(self.other, dt.datetime):
			return (dt_obj.year == self.other.year and dt_obj.month == self.other.month and dt_obj.day == self.other.day and dt_obj.hour == self.other.hour and dt_obj.minute == self.other.minute and dt_obj.second == self.other.second)
		else:
			return (dt_obj.year == self.other.year and dt_obj.month == self.other.month and dt_obj.day == self.other.day)

# Month name mapping (case-insensitive, 3-letter and full names)
_MONTH_NAME_TO_NUM = {
	'jan': 1, 'january': 1,
	'feb': 2, 'february': 2,
	'mar': 3, 'march': 3,
	'apr': 4, 'april': 4,
	'may': 5,
	'jun': 6, 'june': 6,
	'jul': 7, 'july': 7,
	'aug': 8, 'august': 8,
	'sep': 9, 'sept': 9, 'september': 9,
	'oct': 10, 'october': 10,
	'nov': 11, 'november': 11,
	'dec': 12, 'december': 12,
	1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
}


class DateTimeFilter(Filter):
	"""
	Base class for datetime-based filters (modification/creation).

	This class is not intended to be used directly. Instead, use the `Modified` or `Created` filters
	to declaratively filter files by their modification or creation time components (year, month, etc).
	"""
	def __init__(self, attr, extractor, op, value):
		"""
		Initialize a DateTimeFilter.

		Args:
			attr (str): The stat attribute to use ('st_mtime' or 'st_ctime').
			extractor (callable): Function to extract a datetime part (e.g., lambda dt: dt.year).
			op (callable): Operator function (e.g., operator.eq, operator.in_).
			value: Value to compare against (e.g., 2024, [1,2,3]).
		"""
		self.attr = attr  # 'st_mtime' or 'st_ctime'
		self.extractor = extractor  # function to extract part (year, month, etc)
		self.op = op  # operator function (==, in, etc)
		self.value = value

	def match(self, path: 'pathlib.Path', now=None, stat_result=None):
		if stat_result is None:
			stat_result = path.stat()
		ts = getattr(stat_result, self.attr)
		dt_obj = dt.datetime.fromtimestamp(ts)
		part = self.extractor(dt_obj)
		return self.op(part, self.value)

# Helper operator functions
def _in(a, b):
	return a in b

def _not_in(a, b):
	return a not in b

# Declarative extractor filters
class _DateTimePart(Filter):
	attr = None  # override in subclass
	part = None  # override in subclass
	def __init__(self, op, value):
		self.op = op
		self.value = value
	def match(self, path, now=None, stat_result=None):
		if stat_result is None:
			stat_result = path.stat()
		ts = getattr(stat_result, self.attr)
		dt_obj = dt.datetime.fromtimestamp(ts)
		part_value = getattr(dt_obj, self.part)
		return self.op(part_value, self.value)

# Singleton extractor objects with operator overloads
class _DateTimePart:
	def __init__(self, part):
		self.part = part
	def _normalize_month(self, v):
		if isinstance(v, str):
			v_lc = v.strip().lower()
			if v_lc in _MONTH_NAME_TO_NUM:
				return _MONTH_NAME_TO_NUM[v_lc]
			raise ValueError(f"Unknown month name: {v}")
		if isinstance(v, int):
			if v in _MONTH_NAME_TO_NUM:
				return _MONTH_NAME_TO_NUM[v]
			raise ValueError(f"Unknown month number: {v}")
		return v

	def _filter(self, op, value, attr: str = 'st_mtime'):
		class _PartFilter(Filter):
			def match(_, path, now=None, stat_result=None):
				if stat_result is None:
					stat_result = path.stat()
				ts = getattr(stat_result, attr)
				dt_obj = dt.datetime.fromtimestamp(ts)
				part_value = getattr(dt_obj, self.part)
				# Special handling for month: allow string names
				if self.part == 'month':
					val = value
					if isinstance(val, (list, tuple, set)):
						val = [self._normalize_month(v) for v in val]
					else:
						val = self._normalize_month(val)
					return op(part_value, val)
				return op(part_value, value)
		return _PartFilter()

	def __eq__(self, other, attr: str = 'st_mtime'):
		if isinstance(other, (dt.datetime, dt.date)):
			if self.part == 'year':
				return self._filter(operator.eq, other.year, attr=attr)
			if self.part == 'month':
				return self._filter(operator.eq, other.month, attr=attr)
			if self.part == 'day':
				return _DayFilter(other, attr=attr)
			if self.part == 'hour':
				return _HourFilter(other, attr=attr)
			if self.part == 'minute':
				return _MinuteFilter(other)
			if self.part == 'second':
				return _SecondFilter(other)
		# Special handling for month: allow string names
		if self.part == 'month':
			return self._filter(operator.eq, self._normalize_month(other), attr=attr)
		return self._filter(operator.eq, other, attr=attr)

	def __ne__(self, other):
		return self._filter(operator.ne, other)

	def isin(self, items):
		return self._filter(lambda part, values: part in values, items)

	def __call__(self, *args, **kwargs):
		raise TypeError("Do not call Year, Month, etc. Use them as singletons: Year == 2022")

	def __ne__(self, other):
		return self._filter(operator.ne, other)
	def isin(self, items):
		return self._filter(lambda part, values: part in values, items)
	def __call__(self, *args, **kwargs):
		raise TypeError("Do not call Year, Month, etc. Use them as singletons: Year == 2022")

Year = _DateTimePart('year')
Month = _DateTimePart('month')
Day = _DateTimePart('day')
Hour = _DateTimePart('hour')
Minute = _DateTimePart('minute')
Second = _DateTimePart('second')

# Main filter classes

# Accepts either a single filter (e.g., Year == 2022) or (extractor, op, value)
class Modified(Filter):
	"""
	Filter for file modification time (mtime).

	Use this filter to match files based on their modification time components (year, month, day, etc).
	You can pass a single filter (e.g., Modified(Year == 2024)), or use the advanced form:
		Modified(lambda dt: dt.month, operator.eq, 12)

	Args:
		*args: Either a single Filter (e.g., Year == 2024), or (extractor, op, value).
	"""
	def __init__(self, *args):
		"""
		Initialize a Modified filter.

		Args:
			*args: Either a single Filter (e.g., Year == 2024), or (extractor, op, value).
				- If a single Filter is provided, it will be used directly.
				- If three arguments are provided, they are (extractor, op, value).
		"""
		if len(args) == 1 and isinstance(args[0], _DateTimePart):
			# Pass attr explicitly for Modified
			self._filter = args[0].__eq__(args[0], attr='st_mtime')
			self._is_wrapped = True
		elif len(args) == 1 and isinstance(args[0], Filter):
			self._filter = args[0]
			self._is_wrapped = True
		elif len(args) == 3:
			self.base = DateTimeFilter('st_mtime', *args)
			self._is_wrapped = False
		else:
			raise TypeError("Modified expects either (extractor, op, value) or a single Filter (e.g., Modified(Year == 2022))")
	def match(self, path, now=None, stat_result=None):
		if self._is_wrapped:
			return self._filter.match(path, now, stat_result)
		else:
			return self.base.match(path, now, stat_result)

class Created(Filter):
	"""
	Filter for file creation time (ctime).

	Use this filter to match files based on their creation time components (year, month, day, etc).
	You can pass a single filter (e.g., Created(Year == 2024)), or use the advanced form:
		Created(lambda dt: dt.month, operator.eq, 12)

	Args:
		*args: Either a single Filter (e.g., Year == 2024), or (extractor, op, value).
	"""
	def __init__(self, *args):
		"""
		Initialize a Created filter.

		On macOS and platforms that support it, this filter uses st_birthtime (true creation time).
		On other platforms, it falls back to st_ctime (inode change time), which may not be true creation time.
		This is the most cross-platform way to represent file creation time in Python.

		Args:
			*args: Either a single Filter (e.g., Year == 2024), or (extractor, op, value).
				- If a single Filter is provided, it will be used directly.
				- If three arguments are provided, they are (extractor, op, value).
		"""
		# Determine which stat attribute to use for creation time
		import sys
		if sys.platform == "darwin":
			# On macOS, st_birthtime is available
			attr = 'st_birthtime'
		else:
			# On other platforms, use st_ctime
			attr = 'st_ctime'
		if len(args) == 1 and isinstance(args[0], _DateTimePart):
			self._filter = args[0].__eq__(args[0], attr=attr)
			self._is_wrapped = True
		elif len(args) == 1 and isinstance(args[0], Filter):
			self._filter = args[0]
			self._is_wrapped = True
		elif len(args) == 3:
			self.base = DateTimeFilter(attr, *args)
			self._is_wrapped = False
		else:
			raise TypeError("Created expects either (extractor, op, value) or a single Filter (e.g., Created(Year == 2022))")
	def match(self, path, now=None, stat_result=None):
		if self._is_wrapped:
			return self._filter.match(path, now, stat_result)
		else:
			return self.base.match(path, now, stat_result)

# Example usage:
# Modified(lambda dt: dt.month, operator.eq, 12)
# Created(lambda dt: dt.hour, operator.in_, [1,2,3])
