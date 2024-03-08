from . import fake_client
import requests_mock
import pytest
from panther_seim.exceptions import PantherError, EntityAlreadyExistsError, EntityNotFoundError

URL = f"https://api.{fake_client.domain}/data_models"

# --  CREATE

def test_create_200():
    """Successfully created data model."""
    with requests_mock.Mocker() as m:
        m.post(URL, status_code=200, json={})
        fake_client.data_models.create("")

def test_create_400():
    """Cannot create because parameters are invalid."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.post(URL, status_code=400, text="error")
            fake_client.data_models.create("")

def test_create_409():
    """Cannot create because ID is already in use."""
    with pytest.raises(EntityAlreadyExistsError):
        with requests_mock.Mocker() as m:
            m.post(URL, status_code=409, text="error")
            fake_client.data_models.create("")

# -- GET

def test_get_200():
    """Fetched the data model successfully."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}/my_id", status_code=200, json={})
        fake_client.data_models.get("my_id")

def test_get_404():
    """Item cannot be found."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/my_id", status_code=404, json={})
            fake_client.data_models.get("my_id")

# -- UPDATE

def test_update_200():
    """Update, not caring if it exists or not."""
    with requests_mock.Mocker() as m:
        m.put(f"{URL}/my_id", status_code=200, json={})
        fake_client.data_models.update("my_id")

def test_update_200_update_only():
    """Updated an item that is confirmed to exist."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}/my_id", status_code=200, json={}) # item already exists
        m.put(f"{URL}/my_id", status_code=200, json={})
        fake_client.data_models.update("my_id", update_only=True)

def test_update_201():
    """New item created, since there wasn't an existing model with that ID."""
    with requests_mock.Mocker() as m:
        m.put(f"{URL}/my_id", status_code=201, json={})
        fake_client.data_models.update("my_id")

def test_update_201_update_only():
    """Trying to update an item that doesn't exist."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/my_id", status_code=404, json={})
            m.put(f"{URL}/my_id", status_code=201, json={})
            fake_client.data_models.update("my_id", update_only=True)

def test_update_400():
    """Improper update request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.put(f"{URL}/my_id", status_code=400, text="error")
            fake_client.data_models.update("my_id")

# -- DELETE
            
def test_delete_204():
    """Successfull delete operation."""
    with requests_mock.Mocker() as m:
        m.delete(f"{URL}/my_id", status_code=204)
        fake_client.data_models.delete("my_id")

def test_delete_400():
    """Improper delete request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.delete(f"{URL}/my_id", status_code=400)
            fake_client.data_models.delete("my_id")

def test_delete_404():
    """Try to delete non-existing item."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.delete(f"{URL}/my_id", status_code=404)
            fake_client.data_models.delete("my_id")

# -- LIST

def test_list_200():
    """Successful list operation."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}", status_code=200, json={})
        fake_client.data_models.list()