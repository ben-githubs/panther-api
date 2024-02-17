""" Code for interacting with Roles.
"""

from enum import StrEnum
import re
import typing
from gql.transport.exceptions import TransportQueryError
from .exceptions import PantherError, EntityAlreadyExistsError
from ._util import GraphInterfaceBase, UUID_REGEX, to_uuid

class Permission(StrEnum):
    """ This enum class is mostly for ease of use. We won't perform any validation on input using
    this class, and will instead allow the backend to return an error if the permissission passed
    in doesnn't exist. This way, there's no chance of Panther introducing a new permission that
    we can't support.
    """
    AlertModify = "AlertModify"
    AlertRead = "AlertRead"
    BulkUpload = "BulkUpload"
    CloudsecSourceModify = "CloudsecSourceModify"
    CloudsecSourceRead = "CloudsecSourceRead"
    DataAnalyticsModify = "DataAnalyticsModify"
    DataAnalyticsRead = "DataAnalyticsRead"
    DestinationModify = "DestinationModify"
    DestinationRead = "DestinationRead"
    GeneralSettingsModify = "GeneralSettingsModify"
    GeneralSettingsRead = "GeneralSettingsRead"
    LogSourceModify = "LogSourceModify"
    LogSourceRawDataRead = "LogSourceRawDataRead"
    LogSourceRead = "LogSourceRead"
    LookupModify = "LookupModify"
    LookupRead = "LookupRead"
    OrganizationAPITokenModify = "OrganizationAPITokenModify"
    OrganizationAPITokenRead = "OrganizationAPITokenRead"
    PolicyModify = "PolicyModify"
    PolicyRead = "PolicyRead"
    ResourceModify = "ResourceModify"
    ResourceRead = "ResourceRead"
    RuleModify = "RuleModify"
    RuleRead = "RuleRead"
    SummaryRead = "SummaryRead"
    UserModify = "UserModify"
    UserRead = "UserRead"

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
    
    def create(
            self,
            name: str,
            permissions: typing.List[Permission|str],
            log_type_access: typing.List[str] = None,
            log_type_access_kind: str = "ALLOW_ALL"
    ) -> dict:
        """ Creates a new role.

        Args:
            name (str): The display name of the role to be created.
            permissions (list[str, Permission]): List of permissions the token will grant.
                Each item in the list can be either a string (corresponding to a permission name),
                or a member of the Permission enum class.
            log_type_access (list[str]): List of log types the token is permitted to view.
                If your Panther instance does not have RBAC per Log Type enabled, then this setting
                is ignorred.
            log_type_access_kind (str, default=ALLOW_ALL): How to parse the logTypeAccess argument.
                Allowed values are:
                    ALLOW_ALL: all log types are accessible by this token
                    ALLOW: only log types specified in 'logTypeAccess' can be accessed
                    DENY: all log types EXCEPT those specificed in 'logTypeAccess' can be accessed
                    DENY_ALL: the token cannot access any log types
                If your Panther instance does not have RBAC per Log Type enabled, then this setting
                is ignorred.
        
            Returns:
                The newly-created role object, in dictionary form.
        """
        # -- Validate Input
        validate_create_input(name, permissions, log_type_access, log_type_access_kind)
        
        log_type_access_kind = log_type_access_kind.upper().strip() # Some basic formatting
        # We won't validate the value of `log_type_access_kind`, instead letting the Panther
        #   backend do that.
        
        # -- Invoke API
        vargs = {
            "input": {
                "name": name,
                "permissions": [str(x) for x in permissions],
                "logTypeAccessKind": log_type_access_kind
            }
        }
        # Panther doesn't allog 'logTypeAccess' to be specified when logTypeAccess is set to
        #   'ALLOW_ALL' or 'DENY_ALL'. For that reason, we only include the logTypeAccess
        #   if it's explicitly been passed a value by the user.
        if log_type_access is not None:
            vargs["input"]["logTypeAccess"] = log_type_access

        try:
            result = self.execute_gql("roles/create.gql", vargs)
            return result["createRole"]["role"]
        except TransportQueryError as e:
            msgs = []
            for err in e.errors:
                m = err.get("message", "")
                msgs.append(m)
                if re.match(r"Role '[^']+' already exists", m):
                    raise EntityAlreadyExistsError(m)
            msg = "\n\t".join(msgs)
            raise PantherError(f"Panther encountered the following errors:\n\t{msg}")
    

    def update(
            self,
            roleid: str,
            name: str,
            permissions: typing.List[str|Permission],
            log_type_access: typing.List[str] = None,
            log_type_access_kind: str = "ALLOW_ALL"
    ) -> dict:
        """ Updates an existing role. The provided configuration replaces the existing one.
        Ensure that you specify all desired permissions for the role.

        Args:
            id (str): The ID of the role to update.
                Must be a valid UUID, with dashes.
            name (str): The new display name for the role.
            permissions (list[str, Permission]): all desired permissions for the role.
            log_type_access (list[str]): List of log types the token is permitted to view.
                If your Panther instance does not have RBAC per Log Type enabled, then this setting
                is ignorred.
            log_type_access_kind (str, default=ALLOW_ALL): How to parse the logTypeAccess argument.
                Allowed values are:
                    ALLOW_ALL: all log types are accessible by this token
                    ALLOW: only log types specified in 'logTypeAccess' can be accessed
                    DENY: all log types EXCEPT those specificed in 'logTypeAccess' can be accessed
                    DENY_ALL: the token cannot access any log types
                If your Panther instance does not have RBAC per Log Type enabled, then this setting
                is ignorred.

        Returns:
            A dictionary representing the updated role.
        """
        # -- Validate Input
        validate_create_input(name, permissions, log_type_access, log_type_access_kind)
        roleid = to_uuid(roleid)
        log_type_access_kind = log_type_access_kind.upper().strip() # Some basic formatting
        
        # -- Invoke API
        vargs = {
            "input": {
                "id": roleid,
                "name": name,
                "permissions": [str(x) for x in permissions],
                "logTypeAccessKind": log_type_access_kind
            }
        }
        # Panther doesn't allog 'logTypeAccess' to be specified when logTypeAccess is set to
        #   'ALLOW_ALL' or 'DENY_ALL'. For that reason, we only include the logTypeAccess
        #   if it's explicitly been passed a value by the user.
        if log_type_access is not None:
            vargs["input"]["logTypeAccess"] = log_type_access

        try:
            result = self.execute_gql("roles/update.gql", vargs)
            return result["updateRole"]["role"]
        except TransportQueryError as e:
            msgs = []
            for err in e.errors:
                m = err.get("message", "")
                msgs.append(m)
            msg = "\n\t".join(msgs)
            raise PantherError(f"Panther encountered the following errors:\n\t{msg}")

    def delete(self, roleid: str) -> str:
        """ Removes an existing role.
        
        Args:
            roleid (str): The UUID of the role to be deleted.
        
        Returns:
            The role ID.
        """
        # Validate input
        if not isinstance(roleid, str):
            raise TypeError(f"Role ID must be a string, not '{type(roleid).__name__}'.")
        if not UUID_REGEX.fullmatch(roleid):
            raise ValueError(f"Role ID '{roleid}' is not a valid UUID.")

        # -- Invoke API
        vargs = {
            "input": {
                "id": to_uuid(roleid)
            }
        }
        try:
            result = self.execute_gql("roles/delete.gql", vargs)
            return result["deleteRole"]["id"]
        except TransportQueryError as e:
            # NOTE: Panther doesn't return an error if a role with the given ID doesn't exist, so
            #   we will not raise a ResourceNotFound error.
            msgs = []
            for err in e.errors:
                m = err.get("message", "")
                msgs.append(m)
            msg = "\n\t".join(msgs)
            raise PantherError(f"Panther encountered the following errors:\n\t{msg}")


def validate_create_input(
    name: str,
    permissions: typing.List[Permission|str],
    log_type_access: typing.List[str] = None,
    log_type_access_kind: str = "ALLOW_ALL"
):
    if not isinstance(name, str):
        raise ValueError(f"Name must be a string; got {type(name).__name__}.")
    if not isinstance(permissions, list):
        raise ValueError(
            f"Permissions are not specified in a list; got {type(permissions).__name__}"
        )
    for idx, item in enumerate(permissions):
        if not isinstance(item, str) and not isinstance(item, Permission):
            raise ValueError(
                f"permissions[{idx}] must be either a string or Permission object; "
                f"got {type(item).__name__}"
            )
    if log_type_access is None:
        log_type_access = []
    if not isinstance(log_type_access, list):
        raise ValueError(
            f"log_type_access must be a list of strings; got {type(log_type_access).__name__}"
        )
    for idx, item in enumerate(log_type_access):
        if not isinstance(item, str):
            raise ValueError(
                f"log_type_access[{idx}] must be a string; "
                "got {type(item).__name__}."
            )
    if not isinstance(log_type_access_kind, str):
        raise ValueError(
            f"log_type_access_kind must be a string; got {type(log_type_access_kind).__name__}"
        )