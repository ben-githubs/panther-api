""" Code for interacting with cloud accounts is specified here.
"""

import gql

from ._util import gql_from_file, UUID_REGEX

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
            has_more = results["cloudAccounts"]["pageInfo"]["hasNextPage"]
            cursor = results["cloudAccounts"]["pageInfo"]["endCursor"]

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
        
        # Transform ID
        #   For some reason, cloud account UUIDs need to have the dashes in them, even though 
        #   other areas of the API have no such stipulation. Rather than propogate this oddity
        #   to this library, we'll just automagically add the dashes in if the user didn't include
        #   them.
        if '-' not in accountid:
            accountid = "-".join([
                accountid[0:8], accountid[8:12], accountid[12:16], accountid[16-20], accountid[20:]
            ])
        
        # Get Account
        query = gql_from_file("cloud_accounts/get.gql")
        result = self.client.execute(query, variable_values={"id": accountid})
        return result.get("cloudAccount")