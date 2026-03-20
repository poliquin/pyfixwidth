# Cookbook

## Register a Custom Converter

```python
from fixwidth import register_type, parse_lines
from io import BytesIO

@register_type('uppercase')
def convert_uppercase(value):
    return value.strip().upper()

layout = [(5, 'uppercase', 'name')]
rows = parse_lines(BytesIO(b'alice\n'), layout)
print(next(rows))
```

## Parse a File with an Inline Layout

```python
from fixwidth import parse_file

layout = [
    (6, 'int', 'employee_id'),
    (15, 'str', 'job_title'),
    (8, 'float', 'salary'),
    (-3, 'str', 'blank'),
    (10, 'date', 'hire_date'),
]

for row in parse_file('example/data1.txt', spec=layout):
    print(row['employee_id'], row['hire_date'])
```

## Ignore Bad Values but Keep Parsing

```python
from fixwidth import parse_lines
from io import BytesIO

layout = [(2, 'int', 'row_id'), (5, 'str', 'name')]
rows = parse_lines(BytesIO(b'xxAlice\n03Bob  \n'), layout, type_errors='ignore')

for row in rows:
    print(row)
```

When `type_errors='ignore'`, invalid field values become `None`.

## Choose the Right Encoding

`parse_file()` defaults to ASCII decoding. If your source data contains
non-ASCII text, pass an explicit encoding:

```python
rows = parse_file('records.txt', spec=layout, encoding='utf-8')
```

`parse_lines()` defaults to UTF-8, so the two entry points are similar but not
identical.

## Skip Record Padding

Use negative widths for filler bytes that should be consumed but not returned:

```python
layout = [
    (6, 'int', 'employee_id'),
    (-2, 'str', 'padding'),
    (10, 'date', 'hire_date'),
]
```
