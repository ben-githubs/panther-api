from . import fake_client
from panther_seim.exceptions import EntityNotFoundError
import requests_mock
import pytest

URL = f"https://api.{fake_client.domain}/globals"

# -- LIST

def test_list_200():
    """Successful list operation."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}", status_code=200, json={})
        fake_client.globals.list()

# -- GET

def test_get_200():
    """Fetched the global helper successfully."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}/my_id", status_code=200, json={})
        fake_client.globals.get("my_id")

def test_get_404():
    """Item cannot be found."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/my_id", status_code=404, json={})
            fake_client.globals.get("my_id")