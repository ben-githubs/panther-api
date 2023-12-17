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

@pytest.mark.parametrize(("val", "ans"), [
    ("fd5e590e-79ed-4f12-b826-5d01cfc0333b", "fd5e590e-79ed-4f12-b826-5d01cfc0333b"),
    ("e1903752-9d26-11ee-9289-325096b39f47", "e1903752-9d26-11ee-9289-325096b39f47"),
    ("e83a9b42-9d26-11ee-a90d-325096b39f47", "e83a9b42-9d26-11ee-a90d-325096b39f47"),
    ("fd5e590e79ed4f12b8265d01cfc0333b", "fd5e590e-79ed-4f12-b826-5d01cfc0333b"),
    ("e19037529d2611ee9289325096b39f47", "e1903752-9d26-11ee-9289-325096b39f47"),
    ("e83a9b429d2611eea90d325096b39f47", "e83a9b42-9d26-11ee-a90d-325096b39f47")
])
def test_to_uuid(val, ans):
    assert _util.to_uuid(val) == ans


@pytest.mark.parametrize(("val", "ans"), [
    ("fd5e590e79ed4f12b8265d01cfc0333b", "fd5e590e79ed4f12b8265d01cfc0333b"),
    ("e19037529d2611ee9289325096b39f47", "e19037529d2611ee9289325096b39f47"),
    ("e83a9b429d2611eea90d325096b39f47", "e83a9b429d2611eea90d325096b39f47"),
    ("fd5e590e-79ed-4f12-b826-5d01cfc0333b", "fd5e590e79ed4f12b8265d01cfc0333b"),
    ("e1903752-9d26-11ee-9289-325096b39f47", "e19037529d2611ee9289325096b39f47"),
    ("e83a9b42-9d26-11ee-a90d-325096b39f47", "e83a9b429d2611eea90d325096b39f47")
])
def test_to_hex(val, ans):
    assert _util.to_hex(val) == ans