
import csv
import logging
import sys

from .fixwidth import read_file_format, parse_file


def main(schema, files, output=None, delimiter='\t', ignore_type_errors=False,
         skip_blank_lines=False):
    """Process fixed width files and write to standard output.

    Args:
        schema (str): path to file describing fixed width file layout.
        files (list, str): path(s) to fix width files containing data.
        output (file): file for writing processed data (default is sys.stdout).
        delimiter (str): field delimiter for output.
        ignore_type_errors (bool): replace invalid field data with None.
        skip_blank_lines (bool): whether to ignore blank lines in input data.
    """

    if output is None:
        output = sys.stdout

    if isinstance(files, (str, bytes)):
        # assume we got a single file path instead of a list of paths
        files = [files]

    title, spec = read_file_format(schema)

    writer = csv.DictWriter(
        output,
        delimiter=delimiter,
        fieldnames=[field.name for field in spec if field.width > 0]
    )
    writer.writeheader()

    for fpath in files:

        rows = parse_file(
            fpath,
            spec=spec,
            type_errors='ignore' if ignore_type_errors else 'raise',
            skip_blank_lines=skip_blank_lines
        )

        try:
            writer.writerows(rows)
        except BrokenPipeError:
            if output != sys.stdout:
                raise
            else:
                break

    return spec


if __name__ == '__main__':
    import atexit
    import argparse

    argp = argparse.ArgumentParser(
        prog='pyfixwidth',
        description='Read fixed width files'
    )
    argp.add_argument('schema', help='Path to file describing record layout')
    argp.add_argument('files', nargs='+', help='Paths to data files')
    argp.add_argument('-i', '--ignore-type-errors', action='store_true',
                      help='Set fields that raise errors to None and continue')
    argp.add_argument('-s', '--skip-blank-lines', action='store_true',
                      help='Ignore blank lines in input data')
    argp.add_argument('-d', '--delimiter', default='\t', help='Field separator')
    argp.add_argument('-o', '--output', type=argparse.FileType('w'),
                      default=sys.stdout, help='Output file (default stdout)')
    argp.add_argument('--nolog', action='store_true', help='Do not log warnings')

    opts = argp.parse_args()
    atexit.register(opts.output.close)  # close output file when script ends

    logging.basicConfig(
        level=logging.CRITICAL if opts.nolog else logging.WARNING
    )

    spec = main(opts.schema, opts.files, opts.output, opts.delimiter,
                opts.ignore_type_errors, opts.skip_blank_lines)
