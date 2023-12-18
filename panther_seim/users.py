""" Code for interacting with users is specified here.
"""

import gql
from gql.transport.exceptions import TransportQueryError

from .exceptions import EntityNotFoundError
from ._util import gql_from_file, EMAIL_REGEX, execute_gql


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
    

    def update(
            self,
            userid: str,
            email: str = "",
            givenName: str = "",
            familyName: str = "",
            role_id: str = "",
            role_name: str = ""
    ) -> dict:
        """ Make changes to a user's data.

        Args:
            userid (str): The ID of the user to modify.
            email (str): Optional. A new email address for the user.
            givenName (str): Optional. A new given name for the user.
            familyName (str): Optional. A new family name for the user.
            role_id (str): Optional. The ID of a new role to assign to the user. Cannot be used 
                with 'role_name'.
            role_id (str): Optional. The name of a new role to assign the user. Cannot be used with
                'role_id'.
        
        Returns:
            The modified user object.
        """
        # Validate Input
        if not isinstance(userid, str):
            raise TypeError(f"User ID must be a string; got '{type(userid).__name__}'.")
        if not isinstance(email, str):
            raise TypeError(f"Email must be a string; got '{type(email).__name__}'.")
        if not isinstance(givenName, str):
            raise TypeError(f"Given name must be a string; got '{type(givenName).__name__}'.")
        if not isinstance(familyName, str):
            raise TypeError(f"Family name must be a string; got '{type(familyName).__name__}'.")
        if not isinstance(role_id, str):
            raise TypeError(f"Role ID must be a string; got '{type(role_id).__name__}'.")
        if not isinstance(role_name, str):
            raise TypeError(f"Role name must be a string; got '{type(role_name).__name__}'.")
        
        if role_id and role_name:
            raise ValueError("Cannot specify both 'role_id' and 'role_name'.")
        
        if email and not EMAIL_REGEX.fullmatch(email):
            raise ValueError(f"Invalid email: {email}")
        
        # Perform Query
        variable_input = { "input": {"id": userid} }
        if email: variable_input["input"]['email'] = email
        if givenName: variable_input["input"]['givenName'] = givenName
        if familyName: variable_input["input"]['familyName'] = familyName
        if role_id:
            variable_input["input"]['role'] = {
                "kind": "ID",
                "value": role_id
            }
        if role_name:
            variable_input["input"]['role'] = {
                "kind": "NAME",
                "value": role_name
            }
        
        results = execute_gql("users/update.gql", self.client, variable_input=variable_input)
        return results.get("updateUser")