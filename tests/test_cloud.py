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


class TestCreate:
    class FakeClient:
        def execute(self, query, variable_values = dict()):
            assert isinstance(query, DocumentNode)
            assert isinstance(variable_values, dict)

            return {
                "createCloudAccount": {
                    "cloudAccount": {
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
                }
            }
    
    accounts = panther_seim.cloud_accounts.CloudAccountsInterface(FakeClient())
    
    @pytest.mark.parametrize(("account_id", "audit_role", "label", "kwargs"), [
        (111111111111, "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {}),
        ("222222222222", 11, "Test Account", {}),
        ("333333333333", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", 11, {}),
        ("444444444444", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {'region_ignore': "us-east-1"}),
        ("444444444444", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {'region_ignore': [11]}),
        ("555555555555", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {'resource_regex_ignore': '.*:iam:.*'}),
        ("444444444444", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {'resource_regex_ignore': [11]}),
        ("666666666666", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {'resource_type_ignore': 'AWS.S3Bucket'}),
        ("444444444444", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {'resource_type_ignore': [11]})
    ])
    def test_invalid_type(self, account_id, audit_role, label, kwargs):
        with pytest.raises(TypeError):
            self.accounts.create(account_id, audit_role, label, **kwargs)
    

    @pytest.mark.parametrize(("account_id", "audit_role", "label", "kwargs"), [
        ("1234567890123", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {}),
        ("myaccountid", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {}),
        ("123456789012", "def-not-an-arn", "Test Account", {}),
        ("123456789012", "arn:aws:lambda:us-east-1:123456789012:function:api-function:1", "Test Account", {}),
        ("444444444444", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {'region_ignore': ["fake-region"]})
    ])
    def test_invalid_value(self, account_id, audit_role, label, kwargs):
        with pytest.raises(ValueError):
            self.accounts.create(account_id, audit_role, label, **kwargs)
    

    @pytest.mark.parametrize(("account_id", "audit_role", "label", "kwargs"), [
        ("111111111111", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {}),
        ("222222222222", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {"region_ignore": ["us-east-1", "ca-central-1"]}),
        ("333333333333", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {"resource_regex_ignore": [".*:iam:.*"]}),
        ("444444444444", "arn:aws:iam::111122223333:role/PantherAuditRole-us-west-2", "Test Account", {"resource_type_ignore": ["AWS.S3Bucket"]}),
    ])
    def test_valid_input(self, account_id, audit_role, label, kwargs):
        self.accounts.create(account_id, audit_role, label, **kwargs)