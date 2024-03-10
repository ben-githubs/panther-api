""" Code for managing saved and scheduled queries.

Reference:
    https://docs.panther.com/panther-developer-workflows/api/rest/queries
"""

from .exceptions import PantherError, EntityNotFoundError
from ._util import RestInterfaceBase, get_rest_response, to_uuid

class QueriesInterface(RestInterfaceBase):
    """An interface for working with saved and scheduled queries in Panther. An instance of this 
    class will be attached to the Panther client object."""

    def list(self) -> list[dict]:
        """Lists all queries that are configured in Panther.

        Returns:
            A list of saved and scheduled queries
        """
        # Get Saved Queries
        # pylint: disable=duplicate-code
        queries = []
        limit = 50
        has_more = True
        cursor = None

        while has_more:
            params = {"limit": limit}
            if cursor:
                params["cursor"] = cursor
            resp = self._send_request("get", "queries", params=params)
            results = get_rest_response(resp)
            cursor = results.get("next")
            has_more = cursor
            queries += results.get("results", [])

        return queries

    def get(self, query_id: str) -> dict:
        """Returns the saved query with the provided ID.

        Args:
            query_id (str): The UUID of the global to fetch
        """
        # Validate Input
        query_id = to_uuid(query_id)
        resp = self._send_request("get", f"queries/{query_id}")
        match resp.status_code:
            case 200:
                return get_rest_response(resp)
            case 404:
                msg = f"No query found with ID '{query_id}'"
                raise EntityNotFoundError(msg)
            case _:
                # If none of the status codes above matched, then this is an unknown error.
                raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")