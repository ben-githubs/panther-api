""" Code for managing global helper modules.

Reference:
    https://docs.panther.com/panther-developer-workflows/api/rest/globals
"""

from typing import Sequence, Mapping
from ._util import RestInterfaceBase, get_rest_response
from .exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError

class GlobalInterface(RestInterfaceBase):
    """An interface for working with global helper modules in Panther. An instance of this class
    will be attached to the Panther client object. """

    def list(self) -> list[dict]:
        """Lists all global helpers that are configured in Panther.

        Returns:
            A list of globals
        """
        # Get Global Helpers
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
