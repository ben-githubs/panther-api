""" Code for managing global helper modules.

Reference:
    https://docs.panther.com/panther-developer-workflows/api/rest/globals
"""

from typing import Sequence, Mapping
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
