""" Code for rotating API tokens.
"""

from ._util import GraphInterfaceBase


class TokensInterface(GraphInterfaceBase):
    """An interface for working with API tokens in Panther. An instance of this class will be
    attached to the Panther client object.
    """

    def rotate(self) -> str:
        """Rotates the current API token and returns the new token string. Automatcally updates
        the current Panther client to use the new token value. Note however that the backend takes
        several seconds before the new token value is valid.
        """
        resp = self.execute_gql("tokens/rotate.gql")
        token = resp["rotateAPIToken"]["token"]["value"]

        # -- Update Panther client object
        self.root.token = token
        # To reset the auth for the GQL client, we can just delete the current client. The next GQL
        #   call will trigger a new client to be created, with the new token value for
        #   authentication.
        del self.root._gql_client  # pylint: disable=protected-access

        return token
