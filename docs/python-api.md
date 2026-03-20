# Python API

The public API is intentionally small.

## `read_file_format(path)`

Loads a tab-delimited layout file and returns `(title, spec)`, where `spec` is
a list of `FieldInfo(width, datatype, name)` values.

```python
from fixwidth import read_file_format

title, spec = read_file_format('example/data.layout')
print(title)
```

## `parse_file(path, spec, ...)`

Opens a file in binary mode and yields parsed rows as `OrderedDict` objects.

```python
from fixwidth import parse_file, read_file_format

_, spec = read_file_format('example/data.layout')

for row in parse_file('example/data1.txt', spec=spec, type_errors='ignore'):
    print(row['employee_id'], row['salary'])
```

Important defaults:

* `encoding='ascii'`
* `type_errors='raise'`
* `skip_blank_lines=False`

## `parse_lines(lines, spec, ...)`

Parses an iterable of binary lines. This is useful for tests, streams, and
in-memory data.

```python
from io import BytesIO
from fixwidth import parse_lines

layout = [(2, 'int', 'row_id'), (5, 'str', 'name')]
rows = parse_lines(BytesIO(b'01Bob  \n02Susan\n'), layout)
print(next(rows))
```

Important defaults:

* `encoding='utf-8'`
* `type_errors='raise'`
* `skip_blank_lines=False`

## `DictReader(fileobj, fieldinfo, ...)`

Provides a `csv.DictReader`-like interface for binary file objects.

```python
import fixwidth

with open('example/data1.txt', 'rb') as fh:
    reader = fixwidth.DictReader(fh, 'example/data.layout')
    first = next(reader)
    print(first['job_title'])
```

Notes:

* `fileobj` must be opened in binary read mode.
* `fieldinfo` can be a layout path or a sequence of layout tuples.
* `line_num` increments as rows are consumed.

## `register_type(name)`

Registers a custom converter function in the global converter registry.

```python
from fixwidth import register_type

@register_type('uppercase')
def convert_uppercase(value):
    return value.strip().upper()
```

After registration, use `uppercase` in a layout just like any built-in type.
