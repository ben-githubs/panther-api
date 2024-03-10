""" Testing for gql_scalars.py
"""
from datetime import datetime, timezone as tz
import pytest

from panther_seim._util import parse_datetime


@pytest.mark.parametrize(("value", "expected"), [
    ("2023-12-17T16:59:02.222256709Z", datetime(2023, 12, 17, 16, 59, 2, 222256, tz.utc)),
    ("2023-12-17T16:59:02.22225670Z", datetime(2023, 12, 17, 16, 59, 2, 222256, tz.utc)),
    ("2023-12-17T16:59:02.2222567Z", datetime(2023, 12, 17, 16, 59, 2, 222256, tz.utc)),
    ("2023-12-17T16:59:02.222256Z", datetime(2023, 12, 17, 16, 59, 2, 222256, tz.utc)),
    ("2023-12-17T16:59:02.222Z", datetime(2023, 12, 17, 16, 59, 2, 222000, tz.utc)),
    ("2023-12-17T16:59:02Z", datetime(2023, 12, 17, 16, 59, 2, tzinfo=tz.utc))
])
def test_parse_datetime_valid(value, expected):
    assert parse_datetime(value) == expected
