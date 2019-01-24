
import re
from datetime import datetime


def convert_yesno(val):
    """Convert a yes/no value into a boolean."""

    if not isinstance(val, (str, bytes)):
        raise TypeError('Value must be string or bytes.')

    val = val.lower().strip()

    if val in ('y', 'yes', b'y', b'yes'):
        return True

    elif val in ('n', 'no', b'n', b'no'):
        return False

    else:
        if len(val) == 0:
            return None  # missing data
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

    if re.match(r'[0-9]{4}-[01][0-9]-[0-3][0-9]', datestring):
        # assume ISO 8601
        return datetime.strptime(datestring, '%Y-%m-%d').date()

    if re.match(r'[0-9]{4}[01][0-9][0-3][0-9]', datestring):
        # assume missing '-' in ISO 8601 format
        return datetime.strptime(datestring, '%Y%m%d').date()

    if re.match(r'[0-3][0-9][jfmasond][aepuco][nbrylgptvc][0-9]{4}', datestring):
        # assume DATE9 format
        return datetime.strptime(datestring, '%d%b%Y').date()

    if re.match(r'[0-1][0-9][0-3][0-9][0-9]{2}', datestring):
        # assume MMDDYY format where year is from 20th century
        dt = datetime.strptime(datestring, '%m%d%y')
        if dt.year >= 2000:
            dt.replace(year=dt.year - 100)
        return dt

    raise ValueError('Could not convert {} to date'.format(datestring))


def convert_datetime(datestring, format=None):
    """Convert a string into a datetime."""

    datestring = datestring.strip()

    if len(datestring) == 0:
        return None  # missing data

    if format is not None:
        return datetime.strptime(datestring, format)

    # try ISO 8601

    m = re.match(r"""
        ^([0-9]{4})-?          # year
         ([01][0-9])-?         # month
         ([0-3][0-9])(?:-|\s)  # day
         ([0-2][0-9])[.:]      # hour (24-hour clock)
         ([0-6][0-9])[.:]      # minute
         ([0-6][0-9])[.:]?     # second
         ([0-9]{1,6})?         # optional microseconds
        $""", datestring, re.X)

    if m is not None:

        return datetime(
            *(int(i) if i is not None else 0 for i in m.groups())
        )

    raise ValueError('Could not convert {} to datetime'.format(datestring))


def convert_julian(datestring):
    """Convert string representing Julian calendar date to a date."""

    return convert_date(
        re.sub(r'[\- :.]', '', datestring.strip()),  # remove any delimiter
        format='%Y%j'
    )


CONVERTERS = {
    'str': str,
    'int': int,
    'bool': bool,
    'float': float,
    'yesno': convert_yesno,
    'date': convert_date,
    'datetime': convert_datetime,
    'julian': convert_julian
}
