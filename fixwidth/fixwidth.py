
import csv
import logging
import struct
from collections import OrderedDict, namedtuple

from .converters import CONVERTERS

FieldInfo = namedtuple('FieldInfo', ['width', 'datatype', 'name'])


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


def parse_file(fpath, spec, strip=True, type_errors='raise'):
    """Read data from fixed width file."""

    fieldstruct = struct.Struct(
        ' '.join('{}{}'.format(abs(w), 'x' if w < 0 else 's') for w, *_ in spec)
    )

    colnames = tuple(n for w, t, n in spec if w > 0)
    coltypes = tuple(CONVERTERS[t] for w, t, n in spec if w > 0)

    with open(fpath, 'r') as fh:
        for idx, line in enumerate(fh, start=1):

            data = fieldstruct.unpack_from(line.encode())
            data = tuple(
                s.decode().strip() if strip else s.decode() for s in data
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
                            logging.warning(
                                '%s on line %s of %s', err, idx, fpath
                            )
                        else:
                            logging.critical(
                                '%s on line %s of %s', err, idx, fpath
                            )
                            raise

            yield OrderedDict(zip(colnames, values))
