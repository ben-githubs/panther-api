""" Code for interacting with Roles.
"""

from ._util import GraphInterfaceBase, UUID_REGEX

class RolesInterface(GraphInterfaceBase):
    """An interface for working with roles in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def list(self, name_contains: str = None) -> list[dict]:
        """List all roles in the Panther instance.

        Args:
            name_contains (str, optional): Only roles whos names contain this value will be listed.
                Name matching is not case sensitive.

        Returns:
            A list of roles.
        """
        # Validate Input
        if name_contains is not None:
            if not isinstance(name_contains, str):
                raise TypeError(f"name_contains must be a string; got {type(name_contains).__name__}")

        # Craft GQL Input Params
        vargs = {"sortDir": "ascending"}
        if name_contains is not None:
            vargs["nameContains"] = name_contains

        # Invoke GQL
        result = self.execute_gql("roles/list.gql", vargs={"input": vargs})
        return result.get("roles")
    
    def get(self, roleid: str) -> dict:
        """Retreive all details of a single role

        Args:
            roleid (str): the ID or name of the role you want to fetch.
                It is preferable to fetch roles by ID, since name is not guaraneed to be a unique
                indicator for each role.

        Returns:
            A single role, as a dictionary.
        """

        # Validate input
        if not isinstance(roleid, str):
            raise TypeError(f"Role ID must be a string, not '{type(roleid).__name__}'.")

        # Invoke API
        if not UUID_REGEX.fullmatch(roleid):
            # This is an email
            result = self.execute_gql("roles/get_by_name.gql", {"name": roleid})
            return result.get("roleByName")
        # This is an ID
        result = self.execute_gql("roles/get_by_id.gql", {"id": roleid})
        return result.get("roleById")