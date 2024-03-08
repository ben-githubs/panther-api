from . import fake_client
import requests_mock
import pytest

URL = f"https://api.{fake_client.domain}/globals"

# -- LIST

def test_list_200():
    """Successful list operation."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}", status_code=200, json={})
        fake_client.globals.list()