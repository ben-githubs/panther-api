import requests_mock
import pytest

from panther_seim.exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError, RuleTestFailure
from panther_seim.rules import UnitTest, Mock

from . import fake_client

URL = f"https://api.{fake_client.domain}/rules"

# Sample UUID
fake_rule_id = "Mock.MyRule"

# -- LIST

def test_list_200():
    """Successful list operation."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}", status_code=200, json={})
        fake_client.rules.list()

# -- GET

def test_get_200():
    """Fetched the saved rule successfully."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}/{fake_rule_id}", status_code=200, json={})
        fake_client.rules.get(fake_rule_id)

def test_get_404():
    """Item cannot be found."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/{fake_rule_id}", status_code=404, json={})
            fake_client.rules.get(fake_rule_id)

# -- CREATE

def test_create_200():
    """Item created successfully."""
    with requests_mock.Mocker() as m:
        m.post(URL, status_code=200, json={})
        fake_client.rules.create(fake_rule_id, "", "INFO", ["AWS.CloudTrail"])

def test_create_204():
    """Item created successfully, but no response returned."""
    with requests_mock.Mocker() as m:
        m.post(URL, status_code=204, json={})
        assert fake_client.rules.create(fake_rule_id, "", "INFO", ["AWS.CloudTrail"]) is None

def test_create_400():
    """Invalid create request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}", status_code=400, json={})
            fake_client.rules.create(fake_rule_id, "", "INFO", ["AWS.CloudTrail"])

def test_create_409():
    """RuleID already in use."""
    with pytest.raises(EntityAlreadyExistsError):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}", status_code=409, json={})
            fake_client.rules.create(fake_rule_id, "", "INFO", ["AWS.CloudTrail"])

def test_create_with_failing_test():
    """Ensure that uploads fail if a uniut test doesn't pass"""
    mock = Mock("get_counter", "10")
    test = UnitTest("test", False, {"foo": "bar"}, [mock])

    body = """
    from panther_detection_helpers.caching import get_counter

    def rule(event):
        return False and get_counter()
    """
    response = {
        "message": "you have failing tests",
        "testResults": [ { "errored": False, "passed": False, "name": "test"} ]
    }
    with pytest.raises(RuleTestFailure):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}", status_code=400, json=response, headers={"Content-Type": "application/json"})
            fake_client.rules.create(fake_rule_id, body, "INFO", ["AWS.CloudTrail"], tests=[test])

def test_create_with_erroring_test():
    """Ensure that uploads fail if a uniut test doesn't pass"""
    mock = Mock("get_counter", "10")
    test = UnitTest("test", False, {"foo": "bar"}, [mock])

    body = """
    from panther_detection_helpers.caching import get_counter

    def rule(event):
        return False
    """
    response = {
        "message": "you have failing tests",
        "testResults": [ { "errored": True, "passed": True, "name": "test"} ]
    }
    with pytest.raises(RuleTestFailure):
        with requests_mock.Mocker() as m:
            m.post(f"{URL}", status_code=400, json=response, headers={"Content-Type": "application/json"})
            fake_client.rules.create(fake_rule_id, body, "INFO", ["AWS.CloudTrail"], tests=[test])

## -- UPDATE

def test_update_200():
    """Successful update, not caring if item exists."""
    with requests_mock.Mocker() as m:
        m.get(f"{URL}/{fake_rule_id}", status_code=200, json={})
        m.put(f"{URL}/{fake_rule_id}", status_code=200, json={})
        fake_client.rules.update(fake_rule_id, "", "INFO", ["AWS.CloudTrail"])

def test_update_400():
    """Improper update request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/{fake_rule_id}", status_code=200, json={})
            m.put(f"{URL}/{fake_rule_id}", status_code=400, text="error")
            fake_client.rules.update(fake_rule_id, severity="IGNORE")

def test_update_404():
    """Trying to update an item that doesn't exist."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.get(f"{URL}/{fake_rule_id}", status_code=404, json={})
            fake_client.rules.update(fake_rule_id, severity="HIGH")

# -- DELETE

def test_delete_204():
    """Successfull delete operation."""
    with requests_mock.Mocker() as m:
        m.delete(f"{URL}/{fake_rule_id}", status_code=204)
        fake_client.rules.delete(fake_rule_id)

def test_delete_400():
    """Improper delete request."""
    with pytest.raises(PantherError):
        with requests_mock.Mocker() as m:
            m.delete(f"{URL}/{fake_rule_id}", status_code=400)
            fake_client.rules.delete(fake_rule_id)

def test_delete_404():
    """Try to delete non-existing item."""
    with pytest.raises(EntityNotFoundError):
        with requests_mock.Mocker() as m:
            m.delete(f"{URL}/{fake_rule_id}", status_code=404)
            fake_client.rules.delete(fake_rule_id)