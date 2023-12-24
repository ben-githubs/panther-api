""" Code for interacting with alerts is specified here.
"""

import re

import gql
from typing import List

from ._util import execute_gql, UUID_REGEX, to_uuid, S3_BUCKET_NAME_REGEX, KMS_ARN_REGEX, IAM_ARN_REGEX, AWS_REGIONS

ALLOWED_STREAM_TYPES = {
    "auto": "Auto",
    "cloudwatchlogs": "CloudWatchLogs",
    "json": "JSON",
    "jsonarray": "JsonArray",
    "lines": "Lines"
}
LOG_SOURCE_LABEL = re.compile(r"[\ a-zA-Z\d-]+")

class SourcesInterface:
    """An interface for working with queries in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def __init__(self, client: gql.Client):
        self.client = client
        self.s3 = S3Interface(client)
    

    def list(self) -> List[dict]:
        """Lists all log sources configured in Panther.

        Returns:
            A list of log source integrations.
        """
        # -- Invoke API
        vargs = {
            "cursor": ""
        }
        results = execute_gql("sources/list.gql", self.client, variable_values=vargs)
        # This API call is weird - it is structured as if there is pagination, but there isn't.
        return [edge["node"] for edge in results["sources"]["edges"]]

    def get(self, source_id: str) -> dict:
        """Fetches all information about a single log source.
        
        Args:
            source_id (str): The ID of the log source integration to retrieve.
        
        Returns:
            A dictionary with fields for all attributes of a log source.
        """
        # -- Validate Input
        if not isinstance(source_id, str):
            raise TypeError(
                f"Parameter 'source_id' must be a string; got '{type(source_id).__name__}'."
            )
        if not UUID_REGEX.fullmatch(source_id):
            raise ValueError(f"Query ID '{source_id}' is not a valid UUID.")
        # Searching for queries requires dashes in the UUID
        source_id = to_uuid(source_id)

        # -- Invoke API
        vargs = {
            "id": source_id
        }
        results = execute_gql("sources/get.gql", self.client, variable_values=vargs)

        return results["source"]
    

    def delete(self, source_id: str) -> None:
        """Removes a single log source from Panther.

        Args:
            source_id (str): The ID of the log source integration to delete.
        """
        # -- Validate Input
        if not isinstance(source_id, str):
            raise TypeError(
                f"Parameter 'source_id' must be a string; got '{type(source_id).__name__}'."
            )
        if not UUID_REGEX.fullmatch(source_id):
            raise ValueError(f"Query ID '{source_id}' is not a valid UUID.")
        # Searching for queries requires dashes in the UUID
        source_id = to_uuid(source_id)

        # -- Invoke API
        vargs = {
            "id": source_id
        }
        execute_gql("sources/delete.gql", self.client, variable_values=vargs)
    
class S3Interface():
    def __init__(self, client: gql.Client):
        self.client = client

    def create(
            self,
            label: str,
            account_id: str,
            bucket: str,
            iam_role: str,
            prefix_config: List[dict],
            stream_type: str,
            manage_bucket_notifications: bool,
            kms_key: str = None
        ) -> str:
        """Creates a new S3 custom log source.

        Args:
            label (str): The name of the integration.
            account_id (str): The 12-digit ID of the AWS account the source bucket resides in.
            bucket (str): The name of the S3 bucket.
            iam_role (str): The ARN of the IAM Role Panther can use to read the S3 bucket.
            prefix_config (list[dict]): A list of schema/prefic configurations. Each dictionary
                in the list requires the following fields:
                - prefix (str): The prefix for which this configuration is valid.
                - log_types (list[str]): Log types Panther can use to classify the logs under this 
                    prefix.
                - excluded_prefixes (list[str]): Prefixes within the main prefix that Panther 
                    should ignore when reading logs.
            stream_type (str): The stream type to use for logs. Can be 'auto', 'cloudwatchlogs',
                'json', 'jsonarray', or 'lines'.
            manage_bucket_notifications (bool): Flag for whether Panther should manage the SNS 
                topic notifications. Set to False if you want to set up the notification pipeline
                yourself.
            kms_key (str, optional): The ARN of the KMS key needed to decrypt the bucket contents,
                if the bucket is configured to use KMS encryption.
        
        Returns:
            The ID of the newly-created S3 log source integration.
        """
        # -- Validate
        if not isinstance(label, str):
            raise TypeError(f"'label' must be a string; got '{type(label).__name__}'.")
        if not LOG_SOURCE_LABEL.fullmatch(label):
            raise ValueError(
                f"Invalid label '{label}'. Label can only include alphanumeric characters, "
                "dashes and spaces."
            )

        if not isinstance(account_id, str):
            raise TypeError(f"'account_id' must be a string; got '{type(account_id).__name__}'.")
        if len(account_id) != 12 or not account_id.isdigit():
            raise ValueError(f"Invalid 'account_id': {account_id}")
        
        if not isinstance(bucket, str):
            raise TypeError(f"'bucket' must be a string; got '{type(bucket).__name__}'.")
        if not S3_BUCKET_NAME_REGEX.fullmatch(bucket):
            raise ValueError(f"Invalid 'bucket' value: {bucket} is not a valid S3 bucket name")
        
        if not isinstance(iam_role, str):
            raise TypeError(f"'iam_role' must be a string; got '{type(iam_role).__name__}'.")
        if not IAM_ARN_REGEX.fullmatch(iam_role):
            raise ValueError(f"Invalid 'iam_role': {iam_role}")
        
        if not isinstance(prefix_config, List):
            raise TypeError(f"'prefix_config' must be a list; got '{type(prefix_config).__name__}'.")
        for x, conf in enumerate(prefix_config):
            if not isinstance(conf, dict):
                raise TypeError(
                    f"'prefix_config.{x}' must be a dictionary; got {type(conf).__name__}."
                )
            if "prefix" not in conf:
                raise ValueError(f"'prefix_config.{x}' is missing the required field 'prefix'.")
            if not isinstance(conf["prefix"], str):
                raise TypeError(
                    f"'prefix_config.{x}.prefix must be a string; "
                    f"got {type(conf['prefix']).__name__}."
                )
            if "log_types" not in conf:
                raise ValueError(f"'prefix_config.{x}' is missing the required field 'log_types'.")
            if not isinstance(conf["log_types"], List):
                raise TypeError(
                    f"'prefix_config.{x}.log_types must be a list; "
                    f"got {type(conf['log_types']).__name__}."
                )
            for y, log_type in enumerate(conf["log_types"]):
                if not isinstance(log_type, str):
                    raise TypeError(
                        f"'prefix_config.{x}.log_types.{y} must be a string; "
                        f"got {type(log_type).__name__}."
                    )
            if "excluded_prefixes" not in conf:
                raise ValueError(f"'prefix_config.{x}' is missing the required field 'excluded_prefixes'.")
            if not isinstance(conf["excluded_prefixes"], List):
                raise TypeError(
                    f"'prefix_config.{x}.excluded_prefixes must be a list; "
                    f"got {type(conf['excluded_prefixes']).__name__}."
                )
            for y, prefix in enumerate(conf["excluded_prefixes"]):
                if not isinstance(prefix, str):
                    raise TypeError(
                        f"'prefix_config.{x}.excluded_prefixes.{y} must be a string; "
                        f"got {type(prefix).__name__}."
                    )
        
        if not isinstance(stream_type, str):
            raise TypeError(f"'stream_type' must be a string; got {type(stream_type).__name__}.")
        if stream_type.lower() not in ALLOWED_STREAM_TYPES:
            raise ValueError(f"Invalid 'stream_type': {stream_type}")
        # Auto-convert capitalization to match
        stream_type = ALLOWED_STREAM_TYPES.get(stream_type.lower())
        
        if not isinstance(manage_bucket_notifications, bool):
            raise TypeError(
                "'manage_bucket_notifications' must be a bool; "
                f"got {type(manage_bucket_notifications).__name__}."
            )
        
        if kms_key is not None:
            if not isinstance(kms_key, str):
                raise TypeError(f"'kms_key' must be a string; got '{type(kms_key).__name__}'.")
            if not KMS_ARN_REGEX.fullmatch(kms_key):
                raise ValueError(f"Invalid 'kms_key': {kms_key}")
            # Check regions
            region = kms_key.split(":")[3]
            if region not in AWS_REGIONS:
                raise ValueError(f"Invalid region for 'kms_key': {region}")
            
        # -- Invoke API
        vargs = {
            "awsAccountId": account_id,
            "label": label,
            "logProcessingRole": iam_role,
            "logStreamType": stream_type,
            "managedBucketNotifications": manage_bucket_notifications,
            "s3Bucket": bucket,
            "s3PrefixLogTypes": []
        }
        if kms_key:
            vargs["kmsKey"] = kms_key
        for conf in prefix_config:
            vargs["s3PrefixLogTypes"].append({
                "excludedPrefixes": conf["excluded_prefixes"],
                "logTypes": conf["log_types"],
                "prefix": conf["prefix"]
            })
        
        result = execute_gql(
            "sources/s3/create.gql",
            self.client,
            variable_values = { "input": vargs }
        )
        return result["createS3Source"]["logSource"]["integrationId"]