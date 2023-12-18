""" Code for interacting with users is specified here.
"""

import gql
from gql.transport.exceptions import TransportQueryError

from .exceptions import EntityNotFoundError
from ._util import gql_from_file, EMAIL_REGEX


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


    def get(self, userid: str) -> dict:
        """ Retreive all details of a single user

        Args:
            userid (str): the ID or email of the user you want to fetch.
                It is preferable to fetch users by ID, since email is not guaraneed to be a unique
                indicator for each user.
        
        Returns:
            A single user, as a dictionary.
        """

        # Validate input
        if not isinstance(userid, str):
            raise TypeError(f"User ID must be a string, not '{type(userid).__name__}'.")
        
        # Invoke API
        try:
            if EMAIL_REGEX.fullmatch(userid):
                # This is an email
                query = gql_from_file("users/get_by_email.gql")
                result = self.client.execute(query, variable_values={"email": userid})
                return result.get("userByEmail")
            else:
                # This is an ID
                query = gql_from_file("users/get_by_id.gql")
                result = self.client.execute(query, variable_values={"id": userid})
                return result.get("userById")
        except TransportQueryError as e:
            for err in e.errors:
                msg = err.get("message", "")
                if msg.endswith("does not exist"):
                    raise EntityNotFoundError(msg) from e
            # If we didn't catch the error above, raise the initial error
            raise