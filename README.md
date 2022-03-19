Read Fixed Width Files
======================

Python 3 module for reading fixed width data files and converting the field
contents to appropriate Python types.


## Running the program

The module can be run from the command line as follows:

    python -m fixwidth data.layout data1.txt data2.txt

where `data1.txt` and `data2.txt` contain records and `data.layout` contains
a description of the records and how to parse each field. By default, the
records will be written as tab-separated values to stdout.


## Specifying fixed width layout

The `data.layout` file should be tab-delimited and might look like this:

    employees
    # records on workers and their salaries
     6	int	employee_id
    15	str	job_title
     8	float	salary
    # negative values denote fields to skip when reading data
    -3	str	blank
    10	date	hire_date

The file starts with a title. This could be used to map records to a database
table or file name when using the module from other code. Comments begin with
`#` and must be on their own line. Each line describes a data field. The
first value is the field width, the second value describes how to convert the
data to a Python object, and the third value is a field name.

Note that negative field widths are used to specify text that should be
ignored/discarded when reading the data.

### Data types

The possible values for the second value of the layout (the data type) are:

* `str`: textual data
* `int`: integers
* `float`: floating point numbers
* `bool`: boolean (`True`/`False`) values
* `yesno`: parses values like `Y`, `N`, `Yes`, `No` to a `True`/`False` value
* `date`: dates like `1995-08-23`, `19950823`, or `23aug1995`
* `datetime`: dates with time like `1995-08-23 14:30:00.000`
* `julian`: Julian dates in `YYYYDDD` format where `DDD` is day-of-year

#### Date types

Currently, the `date` and `datetime` types will guess the format of the
date using regular expressions. This could be improved by adding more robust
methods or adding some way to specify a date format in the layout file.

#### Adding more data types

Types are defined in `converters.py` and it is trivial to add more types.
To add a type, apply the `fixwidth.converters.register_type` decorator to
a function that takes string input and returns a single object:

```python

from fixwidth.converters import register_type

@register_type('foo')
def convert_foo(value):
    """Convert any input to the string 'foo!'"""
    return 'foo!'
```

The type `foo` can then be used in layouts like the above column types.


## Usage as a module

There is a `fixwidth.DictReader` class that resembles `csv.DictReader` in
usage, but requires files be opened in binary mode:

```python
import fixwidth

with open('example/data1.txt', 'rb') as fh:
    rdr = fixwidth.DictReader(
        fh,
        fieldinfo='example/data.layout',
        skip_blank_lines=True
    )
    next(rdr)
```

The `fieldinfo` parameter can be a path to a layout file (described above)
or a sequence of tuples describing the columns:

```python

layout = [
    (6, 'int', 'employee_id'),
    (15, 'str', 'job_title'),
    (8, 'float', 'salary'),
    (-3, 'str', 'blank'),
    (10, 'date', 'hire_date')
]

with open('example/data1.txt', 'rb') as fh:
    rdr = fixwidth.DictReader(fh, layout)
```

Alternatively, you can use the functions `read_file_format` and `parse_file`:

```python
from fixwidth import read_file_format, parse_file

# read a layout file describing how records are formatted
title, layout = read_file_format('example/data.layout')

# title is 'employees' for the above layout example
# layout is a list of namedtuple objects with (width, datatype, name)

# parse a data file
rows = parse_file('example/data1.txt', spec=layout, type_errors='ignore')

# type_errors determines what should happen when field content does not
# match the given datatype (e.g. an int column containing 'abc'). Use
# 'ignore' to replace fields with None and 'raise' to raise ValueError.

for r in rows:
    print('Salary for {} is {}'.format(r['employee_id'], r['salary'])

# rows is a generator that yields OrderedDict objects.
```

<!-- vim: tabstop=10
-->
