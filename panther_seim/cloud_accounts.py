""" Code for interacting with cloud accounts is specified here.
"""

import re
import typing
import gql
from gql.transport.exceptions import TransportQueryError
from .exceptions import EntityAlreadyExistsError

from ._util import UUID_REGEX, to_uuid, execute_gql, AWS_REGIONS, ARN_REGEX


class CloudAccountsInterface:
    """An interface for working with users in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def __init__(self, client: gql.Client):
        self.client = client

    def list(self) -> list[dict]:
        """Lists all cloud account integrations that are configured in Panther.

        Returns:
            A list of cloud account integrations
        """
        # Get Cloud Accounts
        accounts = []
        has_more = True
        cursor = None

        while has_more:
            results = execute_gql(
                "cloud_accounts/list.gql", self.client, variable_values={"cursor": cursor}
            )
            accounts.extend([edge["node"] for edge in results["cloudAccounts"]["edges"]])
            has_more = results["cloudAccounts"].get("pageInfo", {}).get("hasNextPage")
            cursor = results["cloudAccounts"].get("pageInfo", {}).get("endCursor")

        return accounts

    def get(self, accountid: str) -> dict:
        """Retreive a single cloud account configuration, based on the ID.

        Args:
            id (str): The UUID corresponding to a desired account.

        Returns:
            The cloud account configuration and metadata.
        """
        # Validate input
        if not isinstance(accountid, str):
            raise TypeError(f"Account ID needs to be a string, not '{type(accountid).__name__}'.")
        if not UUID_REGEX.fullmatch(accountid):
            raise ValueError(f"Invalid account ID: '{accountid}'.")

        # Cloud Accounts need dashes in the ID
        accountid = to_uuid(accountid)

        # Get Account
        result = execute_gql(
            "cloud_accounts/get.gql", self.client, variable_values={"id": accountid}
        )
        return result.get("cloudAccount")

    # pylint: disable=too-many-arguments, too-many-branches
    def create(
        self,
        account_id: str,
        audit_role: str,
        label: str,
        region_ignore: typing.List[str] = None,
        resource_regex_ignore: typing.List[str] = None,
        resource_type_ignore: typing.List[str] = None,
    ) -> str:
        """Creates a new AWS cloud scanning integration.

        Args:
            account_id (str): The AWS Account ID of the account to onboard.
            audit_role (str): The ARN of the IAM role Panther can use to scan your account.
            label (str): The user-friendly name of this integration.
            region_ignore (list[str]): A list of aws regions to ignore when scanning.
            resource_regex_ignore (list[str]): A list of regex patterns. If a resource ARN matches
                this pattern, Panther will ignore it when scanning.
            resource_type_ignore (list[str]): A list of resource types to ignore when scanning.

        Returns:
            The ID of the new cloud account integration.
        """

        # -- Validate Input
        if not isinstance(account_id, str):
            raise TypeError(f"Account ID must be a string; got '{type(account_id).__name__}'.")
        if len(account_id) != 12 or not account_id.isdigit():
            raise ValueError(f"Invalid AWS Account ID: {account_id}")

        if not isinstance(audit_role, str):
            raise TypeError(f"Audit role ARN must be a string; got '{type(audit_role).__name__}'.")
        if not ARN_REGEX.fullmatch(audit_role):
            raise ValueError(
                f"Invalid audit IAM role arn: '{audit_role}' does not match {ARN_REGEX.pattern}"
            )

        if not isinstance(label, str):
            raise TypeError(f"Cloud account label must be a string; got '{type(label).__name__}'.")

        if region_ignore is not None:
            if not isinstance(region_ignore, list):
                raise TypeError(
                    f"Region ignore list must be a list; got '{type(region_ignore).__name__}'."
                )
            for region in region_ignore:
                if not isinstance(region, str):
                    raise TypeError(
                        "Region ignore list has a non-string memeber; "
                        f"got '{type(region).__name__}'."
                    )
                if region not in AWS_REGIONS:
                    raise ValueError(f"Invalid region to ignore: {region}")

        if resource_regex_ignore is not None:
            if not isinstance(resource_regex_ignore, str):
                raise TypeError(
                    "Regex ignore list must be a list; "
                    f"got '{type(resource_regex_ignore).__name__}'."
                )
            for item in resource_regex_ignore:
                if not isinstance(item, str):
                    raise TypeError(
                        f"Regex ignore list has a non-strimg member; got '{type(item).__name__}'."
                    )

        if resource_type_ignore is not None:
            if not isinstance(resource_type_ignore, str):
                raise TypeError(
                    "Resource ignore list must be a list; "
                    f"got '{type(resource_type_ignore).__name__}'."
                )
            # Maintaining a list of supported resources here would be difficult, and for little
            #   benefit. Panther's API doesn't do this anyway, so there's no expectation that we
            #   would.

        # -- Make API Call
        values = {
            "awsAccountId": account_id,
            "awsScanConfig": {"auditRole": audit_role},
            "label": label,
        }
        if region_ignore:
            values["regionIgnoreList"] = region_ignore
        if resource_regex_ignore:
            values["resourceRegexIgnoreList"] = resource_regex_ignore
        if resource_type_ignore:
            values["resourceTypeIgnoreList"] = resource_type_ignore
        try:
            result = execute_gql(
                "cloud_accounts/create.gql", self.client, variable_values={"input": values}
            )
            print(result)
            return result["createCloudAccount"]["cloudAccount"]["id"]
        except TransportQueryError as e:
            for err in e.errors:
                msg = err.get("message", "")
                if re.fullmatch(r"Source account \d{12} already onboarded", msg):
                    raise EntityAlreadyExistsError(msg) from e
            raise

    def delete(self, accountid: str) -> str:
        """Deletes the Panther cloud account integration with the given ID.

        Args:
            accountid (str): The integration ID to delete. Not to be confused with the Account ID.

        Returns:
            The ID of the deleted integration.
        """
        # Validate input
        if not isinstance(accountid, str):
            raise TypeError(f"Account ID needs to be a string, not '{type(accountid).__name__}'.")
        if not UUID_REGEX.fullmatch(accountid):
            raise ValueError(f"Invalid account ID: '{accountid}'.")

        # Cloud Accounts need dashes in the ID
        accountid = to_uuid(accountid)

        # Invoke API
        results = execute_gql(
            "cloud_accounts/delete.gql", self.client, variable_values={"id": accountid}
        )
        print(results)
        return results["deleteCloudAccount"]["id"]

    # pylint: disable=too-many-arguments, too-many-branches
    def update(
        self,
        accountid: str,
        label: str,
        audit_role: str,
        region_ignore: typing.List[str] = None,
        resource_regex_ignore: typing.List[str] = None,
        resource_type_ignore: typing.List[str] = None,
    ) -> str:
        """Make changes to a cloud account integration.

        Args:
            accountid: The ID of the cloud account integration. Not to be confused with the
                12-digit AWS account ID.
            label (str): The desired label of the account.
            audit_role (str): The desired ARN of the IAM role Panther can use to scan the account.
            region_ignore (str, optional): The desired list of AWS regions to ignore when scanning.
            resource_regex_ignore (list[str]): A list of regex patterns. If a resource ARN matches
                this pattern, Panther will ignore it when scanning.
            resource_type_ignore (list[str]): A list of resource types to ignore when scanning.

        Returns:
            The fully-updated cloud account configuration.
        """

        # -- Validate Input
        if not isinstance(accountid, str):
            raise TypeError(f"Account ID needs to be a string, not '{type(accountid).__name__}'.")
        if not UUID_REGEX.fullmatch(accountid):
            raise ValueError(f"Invalid account ID: '{accountid}'.")

        if not isinstance(audit_role, str):
            raise TypeError(f"Audit role ARN must be a string; got '{type(audit_role).__name__}'.")
        if not ARN_REGEX.fullmatch(audit_role):
            raise ValueError(
                f"Invalid audit IAM role arn: '{audit_role}' does not match {ARN_REGEX.pattern}"
            )

        if not isinstance(label, str):
            raise TypeError(f"Cloud account label must be a string; got '{type(label).__name__}'.")

        if region_ignore is not None:
            if not isinstance(region_ignore, list):
                raise TypeError(
                    f"Region ignore list must be a list; got '{type(region_ignore).__name__}'."
                )
            for region in region_ignore:
                if not isinstance(region, str):
                    raise TypeError(
                        "Region ignore list has a non-string memeber; "
                        f"got '{type(region).__name__}'."
                    )
                if region not in AWS_REGIONS:
                    raise ValueError(f"Invalid region to ignore: {region}")

        if resource_regex_ignore is not None:
            if not isinstance(resource_regex_ignore, str):
                raise TypeError(
                    "Regex ignore list must be a list; "
                    f"got '{type(resource_regex_ignore).__name__}'."
                )
            for item in resource_regex_ignore:
                if not isinstance(item, str):
                    raise TypeError(
                        f"Regex ignore list has a non-strimg member; got '{type(item).__name__}'."
                    )

        if resource_type_ignore is not None:
            if not isinstance(resource_type_ignore, str):
                raise TypeError(
                    "Resource ignore list must be a list; "
                    f"got '{type(resource_type_ignore).__name__}'."
                )

        # -- Make API Call
        values = {"id": accountid, "awsScanConfig": {"auditRole": audit_role}, "label": label}
        if region_ignore:
            values["regionIgnoreList"] = region_ignore
        if resource_regex_ignore:
            values["resourceRegexIgnoreList"] = resource_regex_ignore
        if resource_type_ignore:
            values["resourceTypeIgnoreList"] = resource_type_ignore

        result = execute_gql(
            "cloud_accounts/update.gql", self.client, variable_values={"input": values}
        )
        return result["updateCloudAccount"]["cloudAccount"]
