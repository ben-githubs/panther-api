""" Code for interacting with users is specified here.
"""

from ._util import EMAIL_REGEX, GraphInterfaceBase


class UsersInterface(GraphInterfaceBase):
    """An interface for working with users in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def list(self) -> list[dict]:
        """List all users in the Panther instance.

        Returns:
            A list of user descriptions.
        """
        # Get Users
        result = self.execute_gql("users/list.gql")
        return result.get("users")

    def get(self, userid: str) -> dict:
        """Retreive all details of a single user

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
        if EMAIL_REGEX.fullmatch(userid):
            # This is an email
            result = self.execute_gql(
                "users/get_by_email.gql", {"email": userid}
            )
            return result.get("userByEmail")
        # This is an ID
        result = self.execute_gql("users/get_by_id.gql", {"id": userid})
        return result.get("userById")

    # pylint: disable=too-many-arguments, too-many-branches
    def update(
        self,
        userid: str,
        email: str = "",
        given_name: str = "",
        family_name: str = "",
        role_id: str = "",
        role_name: str = "",
    ) -> dict:
        """Make changes to a user's data.

        Args:
            userid (str): The ID of the user to modify.
            email (str): Optional. A new email address for the user.
            given_name (str): Optional. A new given name for the user.
            family_name (str): Optional. A new family name for the user.
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
        if not isinstance(given_name, str):
            raise TypeError(f"Given name must be a string; got '{type(given_name).__name__}'.")
        if not isinstance(family_name, str):
            raise TypeError(f"Family name must be a string; got '{type(family_name).__name__}'.")
        if not isinstance(role_id, str):
            raise TypeError(f"Role ID must be a string; got '{type(role_id).__name__}'.")
        if not isinstance(role_name, str):
            raise TypeError(f"Role name must be a string; got '{type(role_name).__name__}'.")

        if role_id and role_name:
            raise ValueError("Cannot specify both 'role_id' and 'role_name'.")

        if email and not EMAIL_REGEX.fullmatch(email):
            raise ValueError(f"Invalid email: {email}")

        # Perform Query
        variable_input = {"input": {"id": userid}}
        if email:
            variable_input["input"]["email"] = email
        if given_name:
            variable_input["input"]["givenName"] = given_name
        if family_name:
            variable_input["input"]["familyName"] = family_name
        if role_id:
            variable_input["input"]["role"] = {"kind": "ID", "value": role_id}
        if role_name:
            variable_input["input"]["role"] = {"kind": "NAME", "value": role_name}

        results = self.execute_gql("users/update.gql", variable_input)
        return results.get("updateUser")
