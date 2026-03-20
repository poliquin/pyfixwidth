# pyfixwidth

`pyfixwidth` reads fixed-width text files and converts each row into Python
values. It is intentionally small: one package, no runtime dependencies, and a
simple layout format that can be stored alongside the data you ingest.

## Install

```bash
pip install pyfixwidth
```

## Quickstart

```bash
python -m fixwidth example/data.layout example/data1.txt example/data2.txt
```

Expected output:

```text
employee_id	job_title	salary	hire_date
100001	CEO	15000.0	1995-08-23
100002	Programmer	8500.0	2002-11-10
100003	Data Scientist	10000.0	2005-07-01
100004	Sales Rep	5000.0	1999-06-01
100005	Customer Servic	4800.0	2001-12-17
```

## Core Ideas

* A layout file describes each fixed-width field as width, converter, and name.
* Negative widths skip filler bytes in the input.
* Parsed rows are yielded as `OrderedDict` objects.
* Blank field content becomes `None` before conversion.
* `DictReader` expects a binary file object.

## Read Next

* [Layout format](layout-format.md)
* [Python API](python-api.md)
* [CLI usage](cli.md)
* [Cookbook](cookbook.md)
