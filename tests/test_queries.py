import requests_mock
import pytest

from panther_seim.exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError

from . import fake_client

URL = f"https://api.{fake_client.domain}/queries"

# -- LIST

def test_list_200():
    """Successful list operation."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}", status_code=200, json={})
        fake_client.queries.list()

# -- GET

def test_get_200():
    """Fetched the saved query successfully."""
    qid = "11111111-2222-3333-4444-555555555555"
    with requests_mock.Mocker() as m:
        m.get(f"{URL}/{qid}", status_code=200, json={})
        fake_client.queries.get(qid)

def test_get_404():
    """Item cannot be found."""
    qid = "11111111-2222-3333-4444-555555555555"
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/{qid}", status_code=404, json={})
            fake_client.queries.get(qid)

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