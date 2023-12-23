from graphql import DocumentNode
import pytest

from panther_seim.sources import SourcesInterface

class TestGet():
    class FakeClient:
        def execute(self, query, variable_values = dict()):
            assert isinstance(query, DocumentNode)
            assert isinstance(variable_values, dict)

            return {
                "source": {}
            }

    sources = SourcesInterface(FakeClient())

    @pytest.mark.parametrize("source_id", [
        10, # int
        1.1, # float
        None, # NoneType
        [''], # list
        ('',), # tuple,
        {'foo': 'bar'}, # dict
        {'foo', 'bar'}, # set
    ])
    def test_invalid_type(self, source_id):
        with pytest.raises(TypeError):
            self.sources.get(source_id)

    @pytest.mark.parametrize("source_id", [
        "c73bcdcc-2669-4bf6-81d3-e4an73fb11fd",
        "c73bcdcc26694bf681d3e4an73fb11fd",
        "definitely-not-a-uuid"
    ])
    def test_invalid_value(self, source_id):
        with pytest.raises(ValueError):
            self.sources.get(source_id)

    @pytest.mark.parametrize("source_id", [
        "c73bcdcc-2669-4bf6-81d3-e4ae73fb11fd"
    ])
    def test_valid(self, source_id):
        self.sources.get(source_id)

class TestDelete():
    class FakeClient:
        def execute(self, query, variable_values = dict()):
            assert isinstance(query, DocumentNode)
            assert isinstance(variable_values, dict)

            return None

    sources = SourcesInterface(FakeClient())

    @pytest.mark.parametrize("source_id", [
        10, # int
        1.1, # float
        None, # NoneType
        [''], # list
        ('',), # tuple,
        {'foo': 'bar'}, # dict
        {'foo', 'bar'}, # set
    ])
    def test_invalid_type(self, source_id):
        with pytest.raises(TypeError):
            self.sources.delete(source_id)

    @pytest.mark.parametrize("source_id", [
        "c73bcdcc-2669-4bf6-81d3-e4an73fb11fd",
        "c73bcdcc26694bf681d3e4an73fb11fd",
        "definitely-not-a-uuid"
    ])
    def test_invalid_value(self, source_id):
        with pytest.raises(ValueError):
            self.sources.delete(source_id)

    @pytest.mark.parametrize("source_id", [
        "c73bcdcc-2669-4bf6-81d3-e4ae73fb11fd"
    ])
    def test_valid(self, source_id):
        self.sources.delete(source_id)
    
class TestCreateS3():
    class FakeClient:
        def execute(self, query, variable_values = dict()):
            assert isinstance(query, DocumentNode)
            assert isinstance(variable_values, dict)

            return {
                "logSource": {
                    "integrationId": "INTEGRATION_ID"
                }
            }

    sources = SourcesInterface(FakeClient())

    @pytest.mark.parametrize(("label", "account_id", "bucket", "iam_role", "prefix_config", "stream_type", "manage_bucket_notifications", "kms_key"), [
        (
            11,
            "000000000001",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            ""
        ),(
            "api test source",
            2,
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            ""
        ),(
            "api test source",
            "000000000003",
            None,
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            ""
        ),(
            "api test source",
            "000000000004",
            "testbucket-1a5ef9",
            (1,2,3),
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            ""
        ),(
            "api test source",
            "000000000005",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            None,
            "auto",
            True,
            ""
        ),(
            "api test source",
            "000000000006",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": 11,
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            ""
        ),(
            "api test source",
            "000000000007",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": "AWS.CloudTrail",
                "excluded_prefixes": []
            }],
            "auto",
            True,
            ""
        ),(
            "api test source",
            "000000000008",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": None
            }],
            "auto",
            True,
            ""
        ),(
            "api test source",
            "000000000009",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [11],
            "auto",
            True,
            ""
        ),(
            "api test source",
            "000000000010",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            5,
            True,
            ""
        ),(
            "api test source",
            "000000000011",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            "True",
            ""
        ),(
            "api test source",
            "000000000012",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            [None]
        )
    ])
    def test_invalid_type(self, label, account_id, bucket, iam_role, prefix_config, stream_type, manage_bucket_notifications, kms_key):
        with pytest.raises(TypeError):
            self.sources.s3.create(
                label,
                account_id,
                bucket,
                iam_role,
                prefix_config,
                stream_type,
                manage_bucket_notifications,
                kms_key = kms_key
            )
    

    @pytest.mark.parametrize(("label", "account_id", "bucket", "iam_role", "prefix_config", "stream_type", "manage_bucket_notifications", "kms_key"), [
        (
            "api_test_source",
            "000000000001",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            None
        ),(
            "test 2",
            "not a aws id",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            None
        ),(
            "test 3",
            "000000000012",
            "$bad bucket n@me",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            None
        ),(
            "test 4",
            "000000000012",
            "testbucket-1a5ef9",
            "bad iam role arn",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            None
        ),(
            "test 2",
            "000000000012",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "invalid stream type",
            True,
            None
        ),(
            "test 2",
            "000000000012",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            "not a KMS key arn"
        ),(
            "test 2",
            "000000000012",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            "arn:aws:kms:region:111111111111:key/6b9dfd29-bbce-4f1a-a470-ce3db35d48db"
        )
    ])
    def test_invalid_value(self, label, account_id, bucket, iam_role, prefix_config, stream_type, manage_bucket_notifications, kms_key):
        with pytest.raises(ValueError):
            self.sources.s3.create(
                label,
                account_id,
                bucket,
                iam_role,
                prefix_config,
                stream_type,
                manage_bucket_notifications,
                kms_key = kms_key
            )
    

    @pytest.mark.parametrize(("label", "account_id", "bucket", "iam_role", "prefix_config", "stream_type", "manage_bucket_notifications", "kms_key"), [
        (
            "Normal Test",
            "000000000001",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            None
        ),(
            "Empty Prefix Config",
            "000000000001",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [],
            "auto",
            True,
            None
        ),(
            "With KMS Key",
            "000000000001",
            "testbucket-1a5ef9",
            "arn:aws:iam::380117727860:role/panther-log-source",
            [{
                "prefix": "/logs",
                "log_types": [
                    "AWS.CloudTrail"
                ],
                "excluded_prefixes": []
            }],
            "auto",
            True,
            "arn:aws:kms:us-west-2:111122223333:key/6b9dfd29-bbce-4f1a-a470-ce3db35d48db"
        )
    ])
    def test_valid(self, label, account_id, bucket, iam_role, prefix_config, stream_type, manage_bucket_notifications, kms_key):
        source_id = self.sources.s3.create(
            label,
            account_id,
            bucket,
            iam_role,
            prefix_config,
            stream_type,
            manage_bucket_notifications,
            kms_key = kms_key
        )
        assert source_id == "INTEGRATION_ID"