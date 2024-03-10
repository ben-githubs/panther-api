""" Code for managing saved and scheduled queries.

Reference:
    https://docs.panther.com/panther-developer-workflows/api/rest/queries
"""

from ._util import RestInterfaceBase, get_rest_response

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