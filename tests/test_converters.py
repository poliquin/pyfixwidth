
import io
from collections import OrderedDict

from fixwidth.fixwidth import parse_lines
from fixwidth.converters import register_type


def test_custom_type():
    """Check creation of a custom column type."""

    # create a custom type that converts any input to "foo!"
    @register_type('foo')
    def convert_foo(value):
        return 'foo!'

    layout = [
        # describe data layout with width, type, name tuples
        (2, 'int', 'row_id'),
        (5, 'str', 'name'),
        (2, 'foo', 'foo')
    ]

    data = io.BytesIO(b'01Bob  01\n02Susan02\n03Amy  03')

    records = parse_lines(data, layout)

    assert next(records) == OrderedDict([
        ('row_id', 1), ('name', 'Bob'), ('foo', 'foo!')
    ])
    assert next(records) == OrderedDict([
        ('row_id', 2), ('name', 'Susan'), ('foo', 'foo!')
    ])
    assert next(records) == OrderedDict([
        ('row_id', 3), ('name', 'Amy'), ('foo', 'foo!')
    ])
