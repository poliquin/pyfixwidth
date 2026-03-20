# pyfixwidth Agent Notes

## What this package does

`pyfixwidth` parses fixed-width text files into Python values. The public
surface is deliberately small:

* `read_file_format(path)` loads a tab-delimited layout file.
* `parse_file(path, spec, ...)` yields parsed rows from a file on disk.
* `parse_lines(lines, spec, ...)` parses an iterable of binary lines.
* `DictReader(fileobj, fieldinfo, ...)` provides a `csv.DictReader`-like
  iterator for binary streams.
* `register_type(name)` registers custom converters globally.

## Layout grammar

The first line of a layout file is the title. Each later non-comment line is:

1. width
2. datatype
3. field name

Comments begin with `#` and must occupy their own line. Negative widths skip
bytes in the input and do not appear in the yielded rows.

## Built-in datatypes

`str`, `int`, `float`, `bool`, `yesno`, `date`, `datetime`, `julian`, `time`

## Runtime defaults and gotchas

* `DictReader` requires a binary file object.
* `parse_file()` defaults to `encoding='ascii'`.
* `parse_lines()` defaults to `encoding='utf-8'`.
* Blank field content becomes `None` before conversion.
* `type_errors='raise'` is the default. Use `type_errors='ignore'` to keep
  parsing and replace invalid values with `None`.
* `skip_blank_lines=True` skips lines that are empty after removing newline
  characters. Lines containing only spaces still yield a row of `None` values.
* `bool` uses Python truthiness because the converter is `bool()`. Prefer
  `yesno` when the source data literally contains yes/no tokens.

## Typical usage

```python
from fixwidth import read_file_format, parse_file

_, spec = read_file_format('example/data.layout')
for row in parse_file('example/data1.txt', spec=spec):
    print(row)
```
