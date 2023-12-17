""" Code for interacting with cloud accounts is specified here.
"""

import gql

from ._util import gql_from_file, UUID_REGEX, to_uuid

class CloudAccountsInterface:
    """An interface for working with users in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def __init__(self, client: gql.Client):
        self.client = client
    

    def list(self) -> list[dict]:
        # Get Cloud Accounts
        query = gql_from_file("cloud_accounts/list.gql")

        accounts = []
        has_more = True
        cursor = None

        while has_more:
            results = self.client.execute(query, variable_values={'cursor': cursor})
            accounts.extend([edge["node"] for edge in results["cloudAccounts"]["edges"]])
            has_more = results["cloudAccounts"].get("pageInfo", {}).get("hasNextPage")
            cursor = results["cloudAccounts"].get("pageInfo", {}).get("endCursor")

        return accounts
    
    def get(self, accountid: str) -> dict:
        """ Retreive a single cloud account configuration, based on the ID.

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
        query = gql_from_file("cloud_accounts/get.gql")
        result = self.client.execute(query, variable_values={"id": accountid})
        return result.get("cloudAccount")