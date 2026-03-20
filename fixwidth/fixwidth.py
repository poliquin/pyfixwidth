"""Core helpers for reading fixed-width text data."""

import csv
import os
import logging
import struct
from collections import OrderedDict, namedtuple

from .converters import CONVERTERS

FieldInfo = namedtuple('FieldInfo', ['width', 'datatype', 'name'])
logger = logging.getLogger('fixwidth')


def read_file_format(fpath):
    """Load a tab-delimited layout description from disk.

    Args:
        fpath (str): Path to a layout file. The first line is treated as the
            layout title. Each later, non-comment line must contain a field
            width, converter name, and field name separated by tabs.

    Returns:
        tuple[str, list[FieldInfo]]: The layout title and a list of
        :class:`FieldInfo` objects.

    Notes:
        Comment lines must begin with ``#`` and occupy their own line.
        Negative widths are allowed and mean "skip these bytes in the input".
    """

    spec = []

    with open(fpath, 'r') as fh:

        # get the name for this format
        title = next(fh).strip()

        rdr = csv.reader(fh, delimiter='\t')
        for i in rdr:

            # ignore comments
            if i[0].strip().startswith('#'):
                continue

            spec.append(FieldInfo(
                int(i[0]),     # field length
                i[1].strip(),  # value type
                i[2].strip()   # field name
            ))

    return title, spec


def parse_lines(lines, spec, strip=True, type_errors='raise', encoding='utf-8',
                src_file=None, skip_blank_lines=False):
    """Parse an iterable of binary lines using a fixed-width specification.

    Args:
        lines (iterable[bytes]): Input records, typically from a binary file
            handle or :class:`io.BytesIO`.
        spec (sequence[tuple]): Sequence of ``(width, datatype, name)`` values
            or :class:`FieldInfo` objects.
        strip (bool): Strip decoded field values before conversion.
        type_errors (str): ``'raise'`` to propagate conversion failures or
            ``'ignore'`` to log a warning and replace the field with ``None``.
        encoding (str): Character encoding used to decode field bytes.
        src_file (str | None): Optional file name used in log messages.
        skip_blank_lines (bool): Skip lines that are empty after removing
            trailing newline characters. Lines that contain only spaces are not
            skipped.

    Yields:
        collections.OrderedDict: One parsed record per input line, excluding
        fields with negative widths.

    Raises:
        ValueError: If a converter fails and ``type_errors='raise'``.
        struct.error: If an input line is shorter than the declared layout.

    Example:
        >>> from io import BytesIO
        >>> layout = [(2, 'int', 'row_id'), (5, 'str', 'name')]
        >>> rows = parse_lines(BytesIO(b'01Bob  \\n'), layout)
        >>> next(rows)['name']
        'Bob'
    """

    fieldstruct = struct.Struct(
        ' '.join('{}{}'.format(abs(w), 'x' if w < 0 else 's') for w, *_ in spec)
    )

    colnames = tuple(n for w, t, n in spec if w > 0)
    coltypes = tuple(CONVERTERS[t] for w, t, n in spec if w > 0)

    for idx, line in enumerate(lines, start=1):

        if skip_blank_lines and len(line.rstrip(b'\r\n')) == 0:
            continue

        data = fieldstruct.unpack_from(line)
        data = tuple(
            s.decode(encoding).strip() if strip else s.decode(encoding) for s in data
        )

        values = []
        for func, v in zip(coltypes, data):
            if len(v.strip()) == 0:
                values.append(None)
            else:
                try:
                    values.append(func(v))
                except ValueError as err:
                    if type_errors == 'ignore':
                        values.append(None)
                        logger.warning(
                            '%s on line %s%s',
                            err,
                            idx,
                            ' of %s' % src_file if src_file is not None else ''
                        )
                    else:
                        logger.critical(
                            '%s on line %s%s',
                            err,
                            idx,
                            ' of %s' % src_file if src_file is not None else ''
                        )
                        raise

        yield OrderedDict(zip(colnames, values))


def parse_file(fpath, spec, strip=True, type_errors='raise', encoding='ascii',
               skip_blank_lines=False):
    """Open and parse a fixed-width data file.

    Args:
        fpath (str): Path to a file containing fixed-width records.
        spec (sequence[tuple]): Sequence of ``(width, datatype, name)`` values
            or :class:`FieldInfo` objects.
        strip (bool): Strip decoded field values before conversion.
        type_errors (str): ``'raise'`` to propagate conversion failures or
            ``'ignore'`` to replace invalid fields with ``None``.
        encoding (str): Character encoding used to decode each field. This
            function defaults to ``'ascii'`` for backward compatibility.
        skip_blank_lines (bool): Skip lines that are empty after removing
            trailing newline characters.

    Yields:
        collections.OrderedDict: Parsed rows from ``fpath``.

    Raises:
        ValueError: If a converter fails and ``type_errors='raise'``.
        struct.error: If a record is shorter than the declared layout.

    Example:
        >>> title, spec = read_file_format('example/data.layout')
        >>> rows = parse_file('example/data1.txt', spec=spec)
        >>> next(rows)['employee_id']
        100001
    """

    with open(fpath, 'rb') as fh:
        yield from parse_lines(
            fh, spec, strip, type_errors, encoding, fpath, skip_blank_lines
        )


class DictReader:
    """Iterate over fixed-width records in a ``csv.DictReader``-like style.

    ``DictReader`` wraps :func:`parse_lines` for a binary file object and keeps
    a ``line_num`` counter like :mod:`csv`. The yielded records omit skipped
    fields with negative widths because parsing is delegated to
    :func:`parse_lines`.

    Attributes:
        fieldnames (tuple[str, ...]): Field names copied from the supplied
            layout specification.
        line_num (int): Number of records read so far.
    """

    def __init__(self, f, fieldinfo, skip_blank_lines=False):
        """Create a reader for a fixed-width binary stream.

        Args:
            f: File-like object opened in binary read mode.
            fieldinfo: Either a path to a layout file or a sequence of layout
                tuples in ``(width, datatype, name)`` form.
            skip_blank_lines (bool): Skip lines that are empty after removing
                trailing newline characters.

        Raises:
            ValueError: If ``fieldinfo`` is a bad path or if ``f`` is not open
                for binary reading.
        """

        try:
            if os.path.isfile(fieldinfo):
                _, self._spec = read_file_format(fieldinfo)
            else:
                raise ValueError('Invalid file {}'.format(fieldinfo))
        except TypeError:
            self._spec = fieldinfo

        if hasattr(f, 'mode') and not ('r' in f.mode and 'b' in f.mode):
            raise ValueError('File must be opened for reading in binary mode')

        self._f = f
        self.line_num = 0
        self.fieldnames = tuple(n for w, t, n in self._spec)
        self._records = parse_lines(
            self._f, self._spec, skip_blank_lines=skip_blank_lines
        )

    def __iter__(self):
        return self

    def __next__(self):
        self.line_num += 1
        return next(self._records)
