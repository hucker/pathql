"""
Date-based PathQL filter presets for common queries.
All functions accept an optional `now` parameter for testability.
"""

import datetime as dt
from pathql.filters.datetimes_ import Modified, Created, Year, Month, Day, Hour, Minute

def modified_this_minute(now: dt.datetime | None = None):
    """Files modified this minute."""
    if now is None:
        now = dt.datetime.now()
    return Modified((Year == now.year) & (Month == now.month) & (Day == now.day) & (Hour == now.hour) & (Minute == now.minute))

def created_this_minute(now: dt.datetime | None = None):
    """Files created this minute."""
    if now is None:
        now = dt.datetime.now()
    return Created((Year == now.year) & (Month == now.month) & (Day == now.day) & (Hour == now.hour) & (Minute == now.minute))



def modified_this_hour(now: dt.datetime | None = None):
    """Files modified this hour."""
    if now is None:
        now = dt.datetime.now()
    return Modified((Year == now.year) & (Month == now.month) & (Day == now.day) & (Hour == now.hour))

def modified_today(now: dt.datetime | None = None):
    """Files modified today."""
    if now is None:
        now = dt.datetime.now()
    return Modified((Year == now.year) & (Month == now.month) & (Day == now.day))

def modified_yesterday(now: dt.datetime | None = None):
    """Files modified yesterday."""
    if now is None:
        now = dt.datetime.now()
    yesterday = now - dt.timedelta(days=1)
    return Modified((Year == yesterday.year) & (Month == yesterday.month) & (Day == yesterday.day))

def modified_this_month(now: dt.datetime | None = None):
    """Files modified this month."""
    if now is None:
        now = dt.datetime.now()
    return Modified((Year == now.year) & (Month == now.month))

def modified_this_year(now: dt.datetime | None = None):
    """Files modified this year."""
    if now is None:
        now = dt.datetime.now()
    return Modified(Year == now.year)


def created_this_hour(now: dt.datetime | None = None):
    """Files created this hour."""
    if now is None:
        now = dt.datetime.now()

    return Created((Year == now.year) & (Month == now.month) & (Day == now.day) & (Hour == now.hour))

def created_today(now: dt.datetime | None = None):
    """Files created today."""
    if now is None:
        now = dt.datetime.now()
    return Created((Year == now.year) & (Month == now.month) & (Day == now.day))

def created_yesterday(now: dt.datetime | None = None):
    """Files created yesterday."""
    if now is None:
        now = dt.datetime.now()
    yesterday = now - dt.timedelta(days=1)
    return Created((Year == yesterday.year) & (Month == yesterday.month) & (Day == yesterday.day))

def created_this_month(now: dt.datetime | None = None):
    """Files created this month."""
    if now is None:
        now = dt.datetime.now()
    return Created((Year == now.year) & (Month == now.month))

def created_this_year(now: dt.datetime | None = None):
    """Files created this year."""
    if now is None:
        now = dt.datetime.now()
    return Created(Year == now.year)
