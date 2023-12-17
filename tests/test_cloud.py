import pytest
from graphql import DocumentNode

import panther_seim.cloud_accounts



class TestGet:
    class FakeClient:
        def execute(self, query, variable_values = dict()):
            assert isinstance(query, DocumentNode)
            assert isinstance(variable_values, dict)

            return {
                "awsAccountId": "111122223333",
                "awsRegionIgnoreList": [],
                "awsScanConfig": {
                    "auditRole": "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2"
                },
                "awsStackName": "panther-cloudsec-setup",
                "createdAt": "2023-08-01T20:34:56.878981785Z",
                "createdBy": {
                    "id": "jane.doe@example.com"
                },
                "id": "fd5e590e-79ed-4f12-b826-5d01cfc0333b",
                "isEditable": True,
                "isRealtimeScanningEnabled": False,
                "label": "Dev Account",
                "lastModifiedAt": None,
                "resourceRegexIgnoreList": [],
                "resourceTypeIgnoreList": []
            }

    accounts = panther_seim.cloud_accounts.CloudAccountsInterface(FakeClient())

    @pytest.mark.parametrize("accountid", [
        123,
        None,
        1.23,
        {'foo': 'bar'}
    ])
    def test_invalid_type(self, accountid: str):
        with pytest.raises(TypeError):
            self.accounts.get(accountid)


    @pytest.mark.parametrize("accountid", [
        "c73bcdcc-2669-4bf6-81d3-e4an73fb11fd",
        "c73bcdcc26694bf681d3e4an73fb11fd",
        "definitely-not-a-uuid"
    ])
    def test_invalid_value(self, accountid: str):
        with pytest.raises(ValueError):
            self.accounts.get(accountid)


    @pytest.mark.parametrize("accountid", [
        "fd5e590e-79ed-4f12-b826-5d01cfc0333b",
        "fd5e590e79ed4f12b8265d01cfc0333b"
    ])
    def test_valid(self, accountid: str):
        self.accounts.get(accountid)