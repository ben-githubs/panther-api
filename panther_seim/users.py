""" Code for interacting with users is specified here.
"""

import gql

from ._util import gql_from_file


class UsersInterface:
    """An interface for working with users in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def __init__(self, client: gql.Client):
        self.client = client

    def list(self) -> list[dict]:
        """ List all users in the Panther instance.

        Returns:
            A list of user descriptions.
        """
        # Get Users
        query = gql_from_file("users/list.gql")
        result = self.client.execute(query)
        return result.get("users")
