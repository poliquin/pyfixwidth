# CLI

`pyfixwidth` can be run either as an installed script or as a module:

```bash
pyfixwidth example/data.layout example/data1.txt
python -m fixwidth example/data.layout example/data1.txt
```

## Usage

```text
usage: pyfixwidth [-h] [-i] [-s] [-d DELIMITER] [-o OUTPUT] [--nolog]
                  schema files [files ...]
```

Arguments:

* `schema`: path to the layout file
* `files`: one or more fixed-width data files

Options:

* `-i`, `--ignore-type-errors`: replace invalid values with `None`
* `-s`, `--skip-blank-lines`: ignore lines that are empty after removing
  trailing newline characters
* `-d`, `--delimiter`: output delimiter, default tab
* `-o`, `--output`: output file path, default standard output
* `--nolog`: suppress warning logs

## Example

```bash
python -m fixwidth example/data.layout example/data1.txt example/data2.txt
```

This writes:

```text
employee_id	job_title	salary	hire_date
100001	CEO	15000.0	1995-08-23
100002	Programmer	8500.0	2002-11-10
100003	Data Scientist	10000.0	2005-07-01
100004	Sales Rep	5000.0	1999-06-01
100005	Customer Servic	4800.0	2001-12-17
```

## Error Handling

By default, conversion failures raise `ValueError`. If you want parsing to
continue, use `--ignore-type-errors`. Invalid fields will become `None` and a
warning will be logged unless `--nolog` is also used.
