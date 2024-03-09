from . import fake_client
from panther_seim.exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError
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

# -- CREATE

def test_create_200():
    """Item created successfully."""
    with requests_mock.Mocker() as m:
        m.post(URL, status_code=200, json={})
        fake_client.globals.create("my_id", "")

def test_create_400():
    """Invalid create request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}", status_code=400, json={})
            fake_client.globals.create("my_id", "")

def test_create_409():
    """Item ID already in use."""
    with pytest.raises(EntityAlreadyExistsError):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}", status_code=409, json={})
            fake_client.globals.create("my_id", "")

## -- UPDATE

def test_update_200():
    """Successful update, not caring if item exists."""
    with requests_mock.Mocker() as m:
        m.put(f"{URL}/my_id", status_code=200, json={})
        fake_client.globals.update("my_id", "")

def test_update_201():
    """New item created, since there wasn't an existing helper with that ID."""
    with requests_mock.Mocker() as m:
        m.put(f"{URL}/my_id", status_code=201, json={})
        fake_client.globals.update("my_id", "")

def test_update_201_update_only():
    """Trying to update an item that doesn't exist."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/my_id", status_code=404, json={})
            m.put(f"{URL}/my_id", status_code=201, json={})
            fake_client.globals.update("my_id", "", update_only=True)

def test_update_400():
    """Improper update request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.put(f"{URL}/my_id", status_code=400, text="error")
            fake_client.globals.update("my_id", "")