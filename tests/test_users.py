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
    
    client = UsersInterface(FakeClient())


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