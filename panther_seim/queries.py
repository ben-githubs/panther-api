""" Code for managing saved and scheduled queries.

Reference:
    https://docs.panther.com/panther-developer-workflows/api/rest/queries
"""

from .exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError
from ._util import RestInterfaceBase, get_rest_response, to_uuid, deep_cast_time

class QueriesInterface(RestInterfaceBase):
    """An interface for working with saved and scheduled queries in Panther. An instance of this 
    class will be attached to the Panther client object."""

    @staticmethod
    def _convert_timestamps(query: dict):
        """Some fields of the query object are timestamps, but are returned as strings. We cast
        them to datetime here."""
        if "createdAt" in query:
            deep_cast_time(query, "createdAt")
        if "updatedAt" in query:
            deep_cast_time(query, "updatedAt")
        return query

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

        # Timestamp conversion
        if self.root.auto_convert:
            queries = [QueriesInterface._convert_timestamps(q) for q in queries]

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
                query = get_rest_response(resp)
                if self.root.auto_convert:
                    query = QueriesInterface._convert_timestamps(query)
                return query
            case 404:
                msg = f"No query found with ID '{query_id}'"
                raise EntityNotFoundError(msg)
            case _:
                # If none of the status codes above matched, then this is an unknown error.
                raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")
    
    @staticmethod
    def _create( # pylint: disable=too-many-arguments
        name: str,
        sql: str,
        desc: str = None,
        sched_cron: str = None,
        sched_rate_mins: int = None,
        sched_disabled: bool = None,
        sched_timeout_mins: int = None
    ) -> dict:
        """Returns the base payload used in the create and update API requests."""

        payload = {
            "name": name,
            "sql": sql
        }
        if desc:
            payload["description"] = desc
        # I am trusting the server to do validation to determine which schedule properties are
        #   required, which are mutually exclusive, etc.
        schedule = {}
        if sched_cron:
            schedule["cron"] = sched_cron
        if sched_rate_mins:
            schedule["rateMinutes"] = sched_rate_mins
        if sched_timeout_mins:
            schedule["timeoutMinutes"] = sched_timeout_mins
        if sched_disabled:
            schedule["disabled"] = sched_disabled
        # Only add 'schedule' to payload if there's any data in it
        if schedule:
            payload["schedule"] = schedule

        return payload
    
    def create( # pylint: disable=too-many-arguments
        self,
        name: str,
        sql: str,
        desc: str = None,
        sched_cron: str = None,
        sched_rate_mins: int = None,
        sched_disabled: bool = None,
        sched_timeout_mins: int = None
    ) -> dict:
        """Saves a new query to Panther.

        Args:
            name (str): The name of the query as displayed in Panther
            sql (str): The raw SQL of the query
            desc (str, optional): A description of the query module
            sched_cron (str, optional): A cron expression to indicate when this query runs
                Can be left blank if you don't want to run this query regularly.
            sched_rate_mins (int, optional): An interval, in minutes, to run this query
                Can be left blank if you don't want to run this query regularly.
            sched_disabled (bool, optional): If True, the query won't run on a schedule
            sched_timeout_mins (int, optional): Upper-limit on query run time
            

        Returns:
            (dict) The created query's metadata
        """
        # Build base payload
        payload = QueriesInterface._create(name, sql, desc, sched_cron, sched_rate_mins, sched_disabled, sched_timeout_mins)

        # Invoke API
        resp = self._send_request("POST", "queries", body=payload)
        match resp.status_code:
            case 200:
                query = get_rest_response(resp)
                if self.root.auto_convert:
                    query = QueriesInterface._convert_timestamps(query)
                return query
            case 400:
                raise PantherError(f"Invalid request: {resp.text}")
            case 409:
                raise EntityAlreadyExistsError(
                    f"Cannot save query; name '{name}' is already in use"
                )

        # If none of the status codes above matched, then this is an unknown error.
        raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")

    def update(  # pylint: disable=too-many-arguments
        self,
        query_id: str,
        name: str,
        sql: str,
        desc: str = None,
        sched_cron: str = None,
        sched_rate_mins: int = None,
        sched_disabled: bool = None,
        sched_timeout_mins: int = None
    ) -> dict:
        """Updates an existing saved query. CANNOT be used to create a new query.

        Args:
            query_id (str): The ID of the query to be updated
            name (str): The name of the query as displayed in Panther
            sql (str): The raw SQL of the query
            desc (str, optional): A description of the query module
            sched_cron (str, optional): A cron expression to indicate when this query runs
                Can be left blank if you don't want to run this query regularly.
            sched_rate_mins (int, optional): An interval, in minutes, to run this query
                Can be left blank if you don't want to run this query regularly.
            sched_disabled (bool, optional): If True, the query won't run on a schedule
            sched_timeout_mins (int, optional): Upper-limit on query run time

        Returns:
            (dict) The new, updated query
        """
        # Ensure ID is a UUID
        query_id = to_uuid(query_id)

        # Build base payload
        payload = QueriesInterface._create(name, sql, desc, sched_cron, sched_rate_mins, sched_disabled, sched_timeout_mins)

        # Invoke API
        resp = self._send_request("POST", f"queries/{query_id}", body=payload)
        match resp.status_code:
            case 200 | 201:
                query = get_rest_response(resp)
                if self.root.auto_convert:
                    query = QueriesInterface._convert_timestamps(query)
                return query
            case 400:
                raise PantherError(f"Invalid request: {resp.text}")
            case 404:
                msg = f"No query found with ID '{query_id}'"
                raise EntityNotFoundError(msg)
            case _:
                # If none of the status codes above matched, then this is an unknown error.
                raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")

    def delete(self, query_id) -> None:
        """Deletes a saved query.

        Args:
            query_id (str): The ID of the saved or scheduled query to delete
        """
        query_id = to_uuid(query_id)
        resp = self._send_request("DELETE", f"queries/{query_id}")

        match resp.status_code:
            case 204:
                return
            case 400:
                raise PantherError(f"Invalid request: {resp.text}")
            case 404:
                raise EntityNotFoundError(
                    f"Cannot delete query with ID {query_id}; ID does not exist"
                )
            case _:
                # If none of the status codes above matched, then this is an unknown error.
                raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")
