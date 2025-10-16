
import datetime as dt
import pathlib
from .base import Filter
import operator

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
	def _filter(self, op, value):
		class _PartFilter(Filter):
			def match(_, path, now=None, stat_result=None):
				if stat_result is None:
					stat_result = path.stat()
				ts = getattr(stat_result, 'st_mtime')
				dt_obj = dt.datetime.fromtimestamp(ts)
				part_value = getattr(dt_obj, self.part)
				return op(part_value, value)
		return _PartFilter()
	def __eq__(self, other):
		if isinstance(other, (dt.datetime, dt.date)):
			if self.part == 'year':
				return self._filter(operator.eq, other.year)
			if self.part == 'month':
				return self._filter(operator.eq, other.month)
			if self.part == 'day':
				# Match year, month, and day
				class _DayFilter(Filter):
					def match(_, path, now=None, stat_result=None):
						if stat_result is None:
							stat_result = path.stat()
						ts = getattr(stat_result, 'st_mtime')
						dt_obj = dt.datetime.fromtimestamp(ts)
						return (dt_obj.year == other.year and dt_obj.month == other.month and dt_obj.day == other.day)
				return _DayFilter()
			if self.part == 'hour':
				class _HourFilter(Filter):
					def match(_, path, now=None, stat_result=None):
						if stat_result is None:
							stat_result = path.stat()
						ts = getattr(stat_result, 'st_mtime')
						dt_obj = dt.datetime.fromtimestamp(ts)
						if isinstance(other, dt.datetime):
							return (dt_obj.year == other.year and dt_obj.month == other.month and dt_obj.day == other.day and dt_obj.hour == other.hour)
						else:
							return (dt_obj.year == other.year and dt_obj.month == other.month and dt_obj.day == other.day)
				return _HourFilter()
			if self.part == 'minute':
				class _MinuteFilter(Filter):
					def match(_, path, now=None, stat_result=None):
						if stat_result is None:
							stat_result = path.stat()
						ts = getattr(stat_result, 'st_mtime')
						dt_obj = dt.datetime.fromtimestamp(ts)
						if isinstance(other, dt.datetime):
							return (dt_obj.year == other.year and dt_obj.month == other.month and dt_obj.day == other.day and dt_obj.hour == other.hour and dt_obj.minute == other.minute)
						else:
							return (dt_obj.year == other.year and dt_obj.month == other.month and dt_obj.day == other.day)
				return _MinuteFilter()
			if self.part == 'second':
				class _SecondFilter(Filter):
					def match(_, path, now=None, stat_result=None):
						if stat_result is None:
							stat_result = path.stat()
						ts = getattr(stat_result, 'st_mtime')
						dt_obj = dt.datetime.fromtimestamp(ts)
						if isinstance(other, dt.datetime):
							return (dt_obj.year == other.year and dt_obj.month == other.month and dt_obj.day == other.day and dt_obj.hour == other.hour and dt_obj.minute == other.minute and dt_obj.second == other.second)
						else:
							return (dt_obj.year == other.year and dt_obj.month == other.month and dt_obj.day == other.day)
				return _SecondFilter()
		return self._filter(operator.eq, other)
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
		if len(args) == 1 and isinstance(args[0], Filter):
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

		Args:
			*args: Either a single Filter (e.g., Year == 2024), or (extractor, op, value).
				- If a single Filter is provided, it will be used directly.
				- If three arguments are provided, they are (extractor, op, value).
		"""
		if len(args) == 1 and isinstance(args[0], Filter):
			self._filter = args[0]
			self._is_wrapped = True
		elif len(args) == 3:
			self.base = DateTimeFilter('st_ctime', *args)
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
