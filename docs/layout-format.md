# Layout Format

A layout file is a tab-delimited text file that describes how to read each
record in a fixed-width source file.

## Structure

The file starts with a title on the first line. Each following, non-comment
line contains three tab-separated values:

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

## Rules

* Comments begin with `#` and must be on their own line.
* Negative widths skip bytes in the source record and do not appear in parsed
  output rows.
* Blank field content becomes `None`.
* Layout files can be loaded with `read_file_format()` or represented directly
  in Python as `(width, datatype, name)` tuples.

## Built-in Converters

| Type | Meaning | Notes |
| --- | --- | --- |
| `str` | decoded text | returns the decoded value unchanged after outer parsing |
| `int` | integer | delegated to `int()` |
| `float` | floating point number | delegated to `float()` |
| `bool` | boolean | delegated to `bool()`, so any non-empty string is `True` |
| `yesno` | yes/no boolean | accepts `y`, `yes`, `n`, `no` |
| `date` | `datetime.date` | infers several common date formats |
| `datetime` | `datetime.datetime` | infers an ISO-like date-time format |
| `julian` | `datetime.date` | parses `YYYYDDD` after removing separators |
| `time` | `datetime.time` | accepts `HH:MM[:SS]`, dotted, and compact forms |

## Date and Time Formats

`date` currently recognizes:

* `YYYY-MM-DD`
* `YYYYMMDD`
* `DDmonYYYY` such as `23aug1995`
* `MMDDYY` with a twentieth-century year assumption
* `YYYY-M-D` without zero padding

`datetime` recognizes an ISO-like form such as
`1995-08-23 14:30:00.000`.

`time` recognizes examples such as `14:30:00`, `14.30.00`, `143000`,
`09:00`, and `0900`.

## Python Layout Example

The same layout can be supplied directly in code:

```python
layout = [
    (6, 'int', 'employee_id'),
    (15, 'str', 'job_title'),
    (8, 'float', 'salary'),
    (-3, 'str', 'blank'),
    (10, 'date', 'hire_date'),
]
```
