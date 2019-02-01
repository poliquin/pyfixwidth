
from datetime import date, datetime
from fixwidth.converters import convert_date


def test_convert_date():
    """Test conversion of dates in typical formats."""

    # ISO 8601
    assert convert_date('1994-10-01') == date(1994, 10, 1)
    assert convert_date('2000-01-01') == date(2000,  1, 1)
    assert convert_date('20031120') == date(2003, 11, 20)
    assert convert_date('19400531') == date(1940,  5, 31)

    # Sloppy ISO 8601 dates without two-digits months and days
    assert convert_date('1994-1-1') == date(1994, 1, 1)
    assert convert_date('2000-8-9') == date(2000, 8, 9)

    # MMDDYY
    assert convert_date('122599') == date(1999, 12, 25)
    assert convert_date('060518') == date(1918,  6,  5)  # assumes 20th century

    # DATE9
    for i, m in enumerate(('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                           'aug', 'sep', 'oct', 'nov', 'dec'), start=1):
        assert convert_date('10{}2018'.format(m)) == date(2018, i, 10)
        assert convert_date('03{}1950'.format(m)) == date(1950, i, 3)
