
import re
from datetime import date
from datetime import datetime
from datetime import time

RE_ISO8601_DATE = re.compile(r'([0-9]{4})-?([01][0-9])-?([0-3][0-9])')
RE_ISO8601_SLOPPY_DATE = re.compile(r'([0-9]{4})-([01]?[0-9])-([0-3]?[0-9])')
RE_DATE9 = re.compile(r'([0-3][0-9])([jfmasond][aepuco][nbrylgptvc])([0-9]{4})')
RE_MMDDYY = re.compile(r'([0-1][0-9])([0-3][0-9])([0-9]{2})')

RE_ISO8601_DATETIME = re.compile(
    r"""
    ^([0-9]{4})-?          # year
     ([01][0-9])-?         # month
     ([0-3][0-9])(?:-|\s)  # day
     ([0-2][0-9])[.:]      # hour (24-hour clock)
     ([0-6][0-9])[.:]      # minute
     ([0-6][0-9])[.:]?     # second
     ([0-9]{1,6})?         # optional microseconds
    $""",
    re.X
)

RE_HMS_TIME = re.compile(r'([0-2][0-9])[.:]?([0-5][0-9])[.:]?([0-5][0-9])?')

MONTHS = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}

YES_VALUES = frozenset(('y', 'yes', b'y', b'yes'))
NO_VALUES = frozenset(('n', 'no', b'n', b'no'))


def convert_yesno(val):
    """Convert a yes/no value into a boolean."""

    val = val.lower().strip()

    if val in YES_VALUES:
        return True

    elif val in NO_VALUES:
        return False

    elif len(val) == 0:
            return None  # missing data

    else:
        if not isinstance(val, (str, bytes)):
            raise TypeError('Value must be string or bytes.')
        else:
            raise ValueError('Invalid value for yes/no field: {}'.format(val))


def convert_date(datestring, format=None):
    """Convert a string into a date."""

    datestring = datestring.strip()

    if len(datestring) == 0:
        return None  # missing data

    if format is not None:
        return datetime.strptime(datestring, format).date()

    # guess the format

    m = RE_ISO8601_DATE.match(datestring)
    if m is not None:
        # assume ISO 8601
        return date(*[int(i) for i in m.groups()])

    m = RE_DATE9.match(datestring)
    if m is not None:
        # assume DATE9 format
        return date(
            int(m.group(3)),
            MONTHS[m.group(2)],
            int(m.group(1))
        )

    m = RE_MMDDYY.match(datestring)
    if m is not None:
        # assume MMDDYY format where year is from 20th century
        return date(
            1900 + int(m.group(3)),
            int(m.group(1)),
            int(m.group(2))
        )

    m = RE_ISO8601_SLOPPY_DATE.match(datestring)
    if m is not None:
        # ISO 8601 without two digit months and days
        return date(*[int(i) for i in m.groups()])

    raise ValueError('Could not convert {} to date'.format(datestring))


def convert_datetime(datestring, format=None):
    """Convert a string into a datetime."""

    datestring = datestring.strip()

    if len(datestring) == 0:
        return None  # missing data

    if format is not None:
        return datetime.strptime(datestring, format)

    # try ISO 8601

    m = RE_ISO8601_DATETIME.match(datestring)

    if m is not None:

        return datetime(
            *[int(i) for i in m.groups(0)]
        )

    raise ValueError('Could not convert {} to datetime'.format(datestring))


def convert_julian(datestring):
    """Convert string representing Julian calendar date to a date."""

    return convert_date(
        re.sub(r'[\- :.]', '', datestring.strip()),  # remove any delimiter
        format='%Y%j'
    )


def convert_time(timestring, format=None):
    """Parse string into a naive time HH:MM:SS."""

    timestring = timestring.strip()

    if len(timestring) == 0:
        return None  # missing data

    if format is not None:
        return datetime.strptime(timestring, format).time()

    m = RE_HMS_TIME.match(timestring)
    if m is not None:
        return time(*[int(i) for i in m.groups(0)])

    raise ValueError('Could not convert {} to time'.format(timestring))


CONVERTERS = {
    'str': lambda x: x,  # argument will already be a string
    'int': int,
    'bool': bool,
    'float': float,
    'yesno': convert_yesno,
    'date': convert_date,
    'datetime': convert_datetime,
    'julian': convert_julian,
    'time': convert_time
}


def register_type(coltype):
    """Create a type for parsing fixed width data."""

    def register(func):
        """Register a function for parsing fixed width data."""

        CONVERTERS[coltype] = func
        return func

    return register
