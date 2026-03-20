# pyfixwidth

`pyfixwidth` reads fixed-width text files and converts each record into Python
values. It can be used as a command-line tool that writes delimited output or
as a small parsing library inside your own code.

The package has no runtime dependencies and is designed to stay lightweight.

## Install

```bash
pip install pyfixwidth
```

## Quickstart

The repository includes a small example layout and sample data files:

```bash
python -m fixwidth example/data.layout example/data1.txt example/data2.txt
```

This writes tab-separated output to standard output:

```text
employee_id	job_title	salary	hire_date
100001	CEO	15000.0	1995-08-23
100002	Programmer	8500.0	2002-11-10
100003	Data Scientist	10000.0	2005-07-01
100004	Sales Rep	5000.0	1999-06-01
100005	Customer Servic	4800.0	2001-12-17
```

If you install the package, the same command is also available as:

```bash
pyfixwidth example/data.layout example/data1.txt example/data2.txt
```

## Layout File Format

A layout file is tab-delimited and describes how each source field should be
read. The first line is a title, then each later line contains:

1. field width
2. converter name
3. field name

Example:

```text
employees
# records on workers and their salaries
  6	int	employee_id
 15	str	job_title
  8	float	salary
# negative values denote fields to skip when reading data
 -3	str	blank
 10	date	hire_date
```

Rules:

* Comments begin with `#` and must occupy their own line.
* Negative widths skip bytes in the input and do not appear in parsed rows.
* Blank field content becomes `None` before type conversion.
* A layout can be loaded from disk with `read_file_format()` or supplied
  directly as a sequence of `(width, datatype, name)` tuples.

### Supported Converters

| Type | Meaning | Accepted values |
| --- | --- | --- |
| `str` | text | any decoded string |
| `int` | integer | values accepted by `int()` |
| `float` | floating point number | values accepted by `float()` |
| `bool` | boolean | Python truthiness via `bool()` |
| `yesno` | yes/no boolean | `Y`, `N`, `Yes`, `No` and lowercase variants |
| `date` | date | `1995-08-23`, `19950823`, `23aug1995`, `1995-8-23`, `122599` |
| `datetime` | date with time | `1995-08-23 14:30:00.000` and similar ISO-like values |
| `julian` | Julian date | `YYYYDDD`, with optional separators removed before parsing |
| `time` | time | `14:30:00`, `14.30.00`, `143000`, `09:00`, `0900` |

`date` and `datetime` formats are inferred with regular expressions, so if you
have unusual source formats you may want to register a custom converter.

## Python API

For most code, these are the main entry points:

* `read_file_format(path)` loads a layout file and returns `(title, spec)`.
* `parse_file(path, spec=...)` yields `OrderedDict` rows from a file on disk.
* `parse_lines(lines, spec=...)` parses an iterable of binary lines.
* `DictReader(fileobj, fieldinfo=...)` provides a `csv.DictReader`-like
  iterator for binary file objects.
* `register_type(name)` lets you add custom converters.

### Parse a Layout and a Data File

```python
from fixwidth import read_file_format, parse_file

title, layout = read_file_format('example/data.layout')

print(title)

rows = parse_file('example/data1.txt', spec=layout, type_errors='ignore')
for row in rows:
    print('Salary for {} is {}'.format(row['employee_id'], row['salary']))
```

### Use `DictReader`

`DictReader` expects a binary file object:

```python
import fixwidth

with open('example/data1.txt', 'rb') as fh:
    reader = fixwidth.DictReader(
        fh,
        fieldinfo='example/data.layout',
        skip_blank_lines=True,
    )
    first_row = next(reader)
    print(first_row['job_title'])
```

You can also pass the layout directly:

```python
layout = [
    (6, 'int', 'employee_id'),
    (15, 'str', 'job_title'),
    (8, 'float', 'salary'),
    (-3, 'str', 'blank'),
    (10, 'date', 'hire_date'),
]

with open('example/data1.txt', 'rb') as fh:
    reader = fixwidth.DictReader(fh, layout)
    print(next(reader))
```

## Custom Converters

Converters live in `fixwidth.converters`. To register a new one, decorate a
function that accepts a decoded string and returns the converted value.

```python
from fixwidth.converters import register_type

@register_type('uppercase')
def convert_uppercase(value):
    return value.strip().upper()
```

After registration, the new type name can be used in layouts just like the
built-in types.

## Troubleshooting

* Open files in binary mode when using `DictReader`.
* `parse_file()` defaults to `encoding='ascii'`.
* `parse_lines()` defaults to `encoding='utf-8'`.
* Use `type_errors='ignore'` to replace invalid values with `None` and keep
  parsing.
* `skip_blank_lines=True` ignores lines that are empty after removing trailing
  newlines. Lines that contain only spaces still produce a row of `None` values.

## More Documentation

Additional documentation lives in [`docs/index.md`](docs/index.md):

* [`docs/layout-format.md`](docs/layout-format.md)
* [`docs/python-api.md`](docs/python-api.md)
* [`docs/cli.md`](docs/cli.md)
* [`docs/cookbook.md`](docs/cookbook.md)
