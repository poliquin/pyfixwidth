
import io
from collections import OrderedDict
from unittest.mock import patch, mock_open

from fixwidth.fixwidth import parse_lines, read_file_format, FieldInfo
from fixwidth.fixwidth import DictReader


def test_file_parsing():
    """Check parsing of fixed width file."""

    layout = [
        # describe data layout with width, type, name tuples
        (2, 'int', 'row_id'),
        (5, 'str', 'name')
    ]

    data = io.BytesIO(b'01Bob  \n02Susan\n03Amy  ')

    records = parse_lines(data, layout)

    assert next(records) == OrderedDict([
        ('row_id', 1), ('name', 'Bob')
    ])
    assert next(records) == OrderedDict([
        ('row_id', 2), ('name', 'Susan')
    ])
    assert next(records) == OrderedDict([
        ('row_id', 3), ('name', 'Amy')
    ])


def test_read_file_format():
    """Check parsing of files describing fixed width layouts."""

    layout = """tablename
        2	int	rowid
        5	str	name\
    """

    # create mock file-like object to override open builtin during test
    m = mock_open(read_data=layout)
    m.return_value.__iter__ = lambda self: self
    m.return_value.__next__ = lambda self: next(iter(self.readline, ''))

    with patch('builtins.open', m):
        title, spec = read_file_format('')

    assert title == 'tablename'
    assert spec[0] == FieldInfo(2, 'int', 'rowid')
    assert spec[1] == FieldInfo(5, 'str', 'name')


def test_dict_reader():
    """Check that DictReader class works like csv.DictReader."""

    layout = [
        # describe data layout with width, type, name tuples
        (2, 'int', 'row_id'),
        (5, 'str', 'name')
    ]

    data = io.BytesIO(b'01Bob  \n02Susan\n03Amy  ')

    records = DictReader(data, layout)

    assert records.fieldnames == ('row_id', 'name')

    assert next(records) == OrderedDict([
        ('row_id', 1), ('name', 'Bob')
    ])
    assert next(records) == OrderedDict([
        ('row_id', 2), ('name', 'Susan')
    ])
    assert next(records) == OrderedDict([
        ('row_id', 3), ('name', 'Amy')
    ])

    assert records.line_num == 3
