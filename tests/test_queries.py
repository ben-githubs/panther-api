import requests_mock
import pytest

from panther_seim.exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError

from . import fake_client

URL = f"https://api.{fake_client.domain}/queries"

# Sample UUID
uuid = "11111111-2222-3333-4444-555555555555"

# -- LIST

def test_list_200():
    """Successful list operation."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}", status_code=200, json={})
        fake_client.queries.list()

# -- GET

def test_get_200():
    """Fetched the saved query successfully."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}/{uuid}", status_code=200, json={})
        fake_client.queries.get(uuid)

def test_get_404():
    """Item cannot be found."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/{uuid}", status_code=404, json={})
            fake_client.queries.get(uuid)

# -- CREATE

def test_create_200():
    """Item created successfully."""
    with requests_mock.Mocker() as m:
        m.post(URL, status_code=200, json={})
        fake_client.queries.create("my_query", "")

def test_create_400():
    """Invalid create request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}", status_code=400, json={})
            fake_client.queries.create("my_query", "")

def test_create_409():
    """Query name already in use."""
    with pytest.raises(EntityAlreadyExistsError):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}", status_code=409, json={})
            fake_client.queries.create("my_query", "")

## -- UPDATE

def test_update_200():
    """Successful update, not caring if item exists."""
    with requests_mock.Mocker() as m:
        m.post(f"{URL}/{uuid}", status_code=200, json={})
        fake_client.queries.update(uuid, "my_query", "")

def test_update_400():
    """Improper update request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}/{uuid}", status_code=400, text="error")
            fake_client.queries.update(uuid, "my_query", "")

def test_update_404():
    """Trying to update an item that doesn't exist."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}/{uuid}", status_code=404, json={})
            fake_client.queries.update(uuid, "my_query", "")

# -- DELETE
            
def test_delete_204():
    """Successfull delete operation."""
    with requests_mock.Mocker() as m:
        m.delete(f"{URL}/{uuid}", status_code=204)
        fake_client.queries.delete(uuid)

def test_delete_400():
    """Improper delete request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.delete(f"{URL}/{uuid}", status_code=400)
            fake_client.queries.delete(uuid)

def test_delete_404():
    """Try to delete non-existing item."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.delete(f"{URL}/{uuid}", status_code=404)
            fake_client.queries.delete(uuid)