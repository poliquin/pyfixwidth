
import csv
import os
import logging
import struct
from collections import OrderedDict, namedtuple

from .converters import CONVERTERS

FieldInfo = namedtuple('FieldInfo', ['width', 'datatype', 'name'])
logger = logging.getLogger('fixwidth')


def read_file_format(fpath):
    """Read file format specification with instructions for parsing data."""

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
                src_file=None):
    """Parse iterable of lines of fixed width data."""

    fieldstruct = struct.Struct(
        ' '.join('{}{}'.format(abs(w), 'x' if w < 0 else 's') for w, *_ in spec)
    )

    colnames = tuple(n for w, t, n in spec if w > 0)
    coltypes = tuple(CONVERTERS[t] for w, t, n in spec if w > 0)

    for idx, line in enumerate(lines, start=1):

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


def parse_file(fpath, spec, strip=True, type_errors='raise', encoding='ascii'):
    """Read data from fixed width file."""

    with open(fpath, 'rb') as fh:
        yield from parse_lines(fh, spec, strip, type_errors, encoding, src_file=fpath)


class DictReader:
    def __init__(self, f, fieldinfo):

        try:
            if os.path.isfile(fieldinfo):
                _, self._spec = read_file_format(fieldinfo)
            else:
                raise ValueError('Invalid file {}'.format(fieldinfo))
        except TypeError:
            self._spec = fieldinfo

        if not ('r' in f.mode and 'b' in f.mode):
            raise ValueError('File must be opened for reading in binary mode')

        self._f = f
        self.line_num = 0
        self.fieldnames = tuple(n for w, t, n in self._spec)
        self._records = parse_lines(self._f, self._spec)

    def __iter__(self):
        return self

    def __next__(self):
        self.line_num += 1
        return next(self._records)
