import requests_mock

from . import fake_client

URL = f"https://api.{fake_client.domain}/queries"

# -- LIST

def test_list_200():
    """Successful list operation."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}", status_code=200, json={})
        fake_client.queries.list()