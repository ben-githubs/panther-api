""" Code for managing global helper modules.

Reference:
    https://docs.panther.com/panther-developer-workflows/api/rest/globals
"""

from typing import Sequence
from ._util import RestInterfaceBase, get_rest_response
from .exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError


class GlobalInterface(RestInterfaceBase):
    """An interface for working with global helper modules in Panther. An instance of this class
    will be attached to the Panther client object."""

    def list(self) -> list[dict]:
        """Lists all global helpers that are configured in Panther.

        Returns:
            A list of globals
        """
        # Get Global Helpers
        # pylint: disable=duplicate-code
        helpers = []
        limit = 50
        has_more = True
        cursor = None

        while has_more:
            params = {"limit": limit}
            if cursor:
                params["cursor"] = cursor
            resp = self._send_request("get", "globals", params=params)
            results = get_rest_response(resp)
            cursor = results.get("next")
            has_more = cursor
            helpers += results.get("results", [])

        return helpers

    def get(self, global_id: str) -> dict:
        """Returns the global helper with the provided ID.

        Args:
            global_id (str): The ID of the global to fetch.
        """

        resp = self._send_request("get", f"globals/{global_id}")
        if resp.status_code == 404:
            msg = f"No globasl found with ID '{global_id}'"
            raise EntityNotFoundError(msg)
        return get_rest_response(resp)

    @staticmethod
    def _create(body: str, desc: str = None, tags: Sequence[str] = None) -> dict:
        """Returns the base payload used in the create and update API requests."""

        payload = {"body": body}
        if desc is not None:
            payload["description"] = desc
        if tags is not None:
            payload["tags"] = tags

        return payload

    def create(
        self, global_id: str, body: str, desc: str = None, tags: Sequence[str] = None
    ) -> dict:
        """Creates a new global helper.

        Args:
            global_id (str): The name of the global helper
            body (str): The Python code of the helper module
            desc (str, optional): A description of the global helper module
            tags (list[str], optional): Any tags to associate with the helper

        Returns:
            (dict) The created helper module
        """
        # Build base payload
        payload = GlobalInterface._create(body, desc, tags)
        payload["id"] = global_id

        # Invoke API
        resp = self._send_request("POST", "globals", body=payload)
        match resp.status_code:
            case 200:
                return get_rest_response(resp)
            case 400:
                raise PantherError(f"Invalid request: {resp.text}")
            case 409:
                raise EntityAlreadyExistsError(
                    f"Cannot craete global; ID '{global_id}' is already in use"
                )

        # If none of the status codes above matched, then this is an unknown error.
        raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")

    def update(  # pylint: disable=too-many-arguments
        self,
        global_id: str,
        body: str,
        desc: str = None,
        tags: Sequence[str] = None,
        update_only: bool = False,
    ) -> dict:
        """Updates an existing global helper.

        Args:
            global_id (str): The ID of the helper to be updated
            body (str): The desired Python code for the helper
            desc (str, optional): A description of the global helper module
            tags (list[str], optional): Any tags to associate with the helper
            update_only (bool, optional): Raise an error if the helper doesn't exist
                By default, if you try to update a helper that doesn't exist, we simply create
                a new helper according to the parameters passed in. If this behaviour is undesirable
                then set update_only to False.

        Returns:
            (dict) The new, updated helper module
        """
        # Build base payload
        payload = GlobalInterface._create(body, desc, tags)
        payload["id"] = global_id

        # Check if item exists
        if update_only:
            self.get(global_id)  # Will raise EntityNotFound if the item doesn't exist yet

        # Invoke API
        resp = self._send_request("PUT", f"globals/{global_id}", body=payload)
        match resp.status_code:
            case 200 | 201:
                return get_rest_response(resp)
            case 400:
                raise PantherError(f"Invalid request: {resp.text}")
            case _:
                # If none of the status codes above matched, then this is an unknown error.
                raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")

    def delete(self, global_id) -> None:
        """Deletes a global helper.

        Args:
            global_id (str): The ID of the global helper to delete
        """
        resp = self._send_request("DELETE", f"globals/{global_id}")

        # pylint: disable=duplicate-code
        match resp.status_code:
            case 204:
                return
            case 400:
                raise PantherError(f"Invalid request: {resp.text}")
            case 404:
                raise EntityNotFoundError(
                    f"Cannot delete global with ID {global_id}; ID does not exist"
                )
            case _:
                # If none of the status codes above matched, then this is an unknown error.
                raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")
