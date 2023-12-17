from datetime import datetime, timezone, timedelta

import pytest

from panther_seim import _util

@pytest.mark.parametrize(("input", "expected"), [
    ("2023-12-11T11:11:11Z", "2023-12-11T11:11:11Z"), # valid string
    (datetime(2023,12,11,11,11,11), "2023-12-11T11:11:11Z"), # datetime without timezone
    (datetime(2023,12,11,23,11,11,tzinfo=timezone(timedelta(hours=12))), "2023-12-11T11:11:11Z"), # datetime with timezone
    (1702314671, "2023-12-11T11:11:11Z") # UNIX timestamp
])
def test_validate_timestamp_valid_input(input, expected):
    assert _util.validate_timestamp(input) == expected


@pytest.mark.parametrize("input", [
    "2023-12-11 11:11:11Z", # no 'T' in string
    "2023-11-11T11:11:11", # no 'Z' at end of string
    0, # Invalid unix timestamp
])
def test_validate_timestamp_invalid_input(input):
    with pytest.raises(ValueError):
        _util.validate_timestamp(input)