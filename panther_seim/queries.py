""" Code for interacting with alerts is specified here.
"""

import time
from typing import List

from panther_seim.exceptions import QueryCancelled, QueryError
from ._util import UUID_REGEX, to_uuid, GraphInterfaceBase


class QueriesInterface(GraphInterfaceBase):
    """An interface for working with queries in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def execute_async(self, sql: str) -> str:
        """Executes a SQL query asynchronously in the data lake. Results can be fetched at a later
        time using the query ID.

        Args:
            sql (str): The SQL code to run as the query.

        Returns:
            The ID of the newly-created query.
        """

        # -- Validate Input
        if not isinstance(sql, str):
            raise TypeError(f"Parameter 'SQL' must be a string; got '{type(sql).__name__}'.")
        # We won't bother validating the SQL syntax, since we can't know what's a valid object name
        #   in the datalake until we compile the SQL.

        # -- API Call
        vargs = {"sql": sql}
        results = self.execute_gql("queries/execute.gql", vargs)
        return results["executeDataLakeQuery"]["id"]

    def results(self, query_id: str) -> tuple[str, str, List[dict]]:
        """Fetches the status of a running query, or the results, if the query is finished.

        Args:
            query_id (str): The ID of the query to fetch.

        Returns:
            status (str): The status of the query. Allowed values are 'cancelled', 'failed',
                'running', and 'succeeded'.
            message (str): A string that describes the current status of the query.
            results (list[dict]): The results the query yielded. This field will be None if the
                query hasn't successully completed.
        """
        # -- Validate
        if not isinstance(query_id, str):
            raise TypeError(
                f"Parameter 'query_id' must be a string; got '{type(query_id).__name__}'."
            )
        if not UUID_REGEX.fullmatch(query_id):
            raise ValueError(f"Query ID '{query_id}' is not a valid UUID.")
        # Searching for queries requires dashes in the UUID
        query_id = to_uuid(query_id)

        # -- API Call
        vargs = {"id": query_id}
        resp = self.execute_gql("queries/results.gql", vargs)

        # If the query hasn't returned results, return the status and message
        results = resp["dataLakeQuery"]
        if results["status"] != "succeeded":
            return results["status"], results["message"], None

        # Else, fetch all the results
        rows = [edge["node"] for edge in results["results"]["edges"]]
        while results.get("pageInfo", {}).get("hasNextPage", False):
            vargs["cursor"] = results["pageInfo"]["endCursor"]
            resp = self.execute_gql("queries/results.gql", vargs)
            results = resp["dataLakeQuery"]
            rows.extend([edge["node"] for edge in results["results"]["edges"]])
        return results["status"], results["message"], rows

    def execute(
        self, sql: str, status_dict: dict = None, refresh: int | float = None
    ) -> List[dict]:
        """Executes a query and waits for it to complete, then fetches the results.

        Args:
            sql (str): The SQL code to run as the query.
            status_dict (dict, optional): A dictionary used to store the most recent query status,
                and message. This is useful for troubleshooting if the query is failing and the
                function isn't returning any data.
            refresh (int, float, optional): How many seconds to wait between checks on the query.
                By default, we poll once per second for the first 20 seconds, and once per ten
                seconds thereafter.

        Returns:
            The query results.
        """
        # -- Validate
        if not isinstance(sql, str):
            raise TypeError(f"Parameter 'SQL' must be a string; got '{type(sql).__name__}'.")
        # We won't bother validating the SQL syntax, since we can't know what's a valid object name
        #   in the datalake until we compile the SQL.

        if status_dict is None:
            status_dict = {}
        if not isinstance(status_dict, dict):
            raise TypeError(
                "Parameter 'status_dict' must be a dictionary; "
                f"got '{type(status_dict).__name__}'."
            )
        if refresh is not None:
            if not any(isinstance(refresh, _type) for _type in (int, float)):
                raise TypeError(
                    "Parameter 'refresh' must be an int or a float; "
                    f"got '{type(refresh).__name__}'."
                )
            if refresh <= 0:
                raise ValueError("Parameter 'refresh' must be greater than zero.")

        # -- API Calls
        # Create the query
        query_id = self.execute_async(sql)
        status, message, results = self.results(query_id)
        status_dict["status"] = status
        status_dict["message"] = message

        n_loops = 0
        while status == "running":
            if refresh is not None:
                time.sleep(refresh)
            else:
                time.sleep(1 if n_loops < 20 else 10)
            status, message, results = self.results(query_id)
            n_loops += 1

        # By now, the query is completed.
        match status:
            case "succeeded":
                return results
            case "cancelled":
                raise QueryCancelled(message)
            case "failed":
                raise QueryError(message)
            case _:
                # Status didn't match any of the expected values
                raise QueryError(f"Query returned with invalid status: {status}")
