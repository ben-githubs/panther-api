""" Code for interacting with cloud accounts is specified here.
"""

import gql

from ._util import gql_from_file, UUID_REGEX, to_uuid, execute_gql


class CloudAccountsInterface:
    """An interface for working with users in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def __init__(self, client: gql.Client):
        self.client = client

    def list(self) -> list[dict]:
        """ Lists all cloud account integrations that are configured in Panther.

        Returns:
            A list of cloud account integrations
        """
        # Get Cloud Accounts
        accounts = []
        has_more = True
        cursor = None

        while has_more:
            results = execute_gql("cloud_accounts/list.gql", self.client, variable_values={"cursor": cursor})
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
        result = execute_gql("cloud_accounts/get.gql", self.client, variable_values={"id": accountid})
        return result.get("cloudAccount")
