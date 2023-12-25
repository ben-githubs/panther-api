import pytest
from graphql import DocumentNode

from panther_seim.users import UsersInterface

class TestGet:
    class FakeClient:
        def execute(self, query, variable_values = dict()):
            assert isinstance(query, DocumentNode)
            assert isinstance(variable_values, dict)

            return {
                "id": "13c7909e-5e8d-4164-93de-5ca1dce28da1",
                "givenName": "Ben",
                "familyName": "Airey 2",
                "email": "ben.airey@panther.com",
                "role": {
                    "name": "Admin",
                    "id": "2c9e630c-7356-45a0-a7a3-f748f6ef92a5",
                    "permissions": [
                        "AlertModify",
                        "BulkUpload",
                        "CloudsecSourceModify",
                        "DataAnalyticsModify",
                        "DestinationModify",
                        "GeneralSettingsModify",
                        "LogSourceModify",
                        "LogSourceRawDataRead",
                        "LookupModify",
                        "OrganizationAPITokenModify",
                        "PolicyModify",
                        "ResourceModify",
                        "RuleModify",
                        "SummaryRead",
                        "UserModify"
                    ]
                },
                "status": "CONFIRMED",
                "createdAt": "2023-08-01T22:09:32Z"
            }
    
    client = UsersInterface(None, FakeClient())

    @pytest.mark.parametrize("val", [
        10, # int
        10.1, # float
        True, # bool
        ["foo", "bar"], # list
        {"foo": "bar"} # dict
    ])
    def test_invalid_input_type(self, val):
        with pytest.raises(TypeError):
            self.client.get(val)
    
    @ pytest.mark.parametrize("val", [
        "this is a id",
        "user@example.com"
    ])
    def test_valid_input(self, val):
        # This shouldn't cause any errors at all.
        self.client.get(val)


class TestUpdate:
    class FakeClient:
        def execute(self, query, variable_values = dict()):
            assert isinstance(query, DocumentNode)
            assert isinstance(variable_values, dict)

            return {
                "id": "13c7909e-5e8d-4164-93de-5ca1dce28da1",
                "givenName": "Ben",
                "familyName": "Airey 2",
                "email": "ben.airey@panther.com",
                "role": {
                    "name": "Admin",
                    "id": "2c9e630c-7356-45a0-a7a3-f748f6ef92a5",
                    "permissions": [
                        "AlertModify",
                        "BulkUpload",
                        "CloudsecSourceModify",
                        "DataAnalyticsModify",
                        "DestinationModify",
                        "GeneralSettingsModify",
                        "LogSourceModify",
                        "LogSourceRawDataRead",
                        "LookupModify",
                        "OrganizationAPITokenModify",
                        "PolicyModify",
                        "ResourceModify",
                        "RuleModify",
                        "SummaryRead",
                        "UserModify"
                    ]
                },
                "status": "CONFIRMED",
                "createdAt": "2023-08-01T22:09:32Z"
            }
    
    client = UsersInterface(None, FakeClient())

    @pytest.mark.parametrize(("userid", "kwargs"), [
        (123, {}),
        ("id", {"email": 123}),
        ("id", {"givenName": 123}),
        ("id", {"familyName": 123}),
        ("id", {"role_id": 123}),
        ("id", {"role_name": 123})
    ])
    def test_invalid_input_type(self, userid, kwargs):
        with pytest.raises(TypeError):
            self.client.update(userid, **kwargs)

    @pytest.mark.parametrize(("userid", "kwargs"), [
        ("id", {"email": "not an email"}),
        ("id", {"role_name": "foo", "role_id": "bar"})
    ])
    def test_invalid_input_value(self, userid, kwargs):
        with pytest.raises(ValueError):
            self.client.update(userid, **kwargs)

    def test_valid_input(self):
        self.client.update(
            "id",
            email="foo.bar@baz.com",
            given_name="foo",
            family_name = "bar",
            role_id = "roleID"
        )