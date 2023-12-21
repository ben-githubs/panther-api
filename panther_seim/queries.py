""" Code for interacting with alerts is specified here.
"""

from typing import List

import gql
from ._util import execute_gql, UUID_REGEX, to_uuid

class QueriesInterface:
    """An interface for working with queries in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def __init__(self, client: gql.Client):
        self.client = client
    
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
        vargs = {
            'sql': sql
        }
        results = execute_gql("queries/execute.gql", self.client, variable_values=vargs)
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
        resp = execute_gql("queries/results.gql", self.client, variable_values=vargs)
        
        # If the query hasn't returned results, return the status and message
        results = resp["dataLakeQuery"]
        if results["status"] != "succeeded":
            return results["status"], results["message"], None
        
        # Else, fetch all the results
        rows = [edge["node"] for edge in results["results"]["edges"]]
        while results.get("pageInfo", {}).get("hasNextPage", False):
            vargs["cursor"] = results["pageInfo"]["endCursor"]
            resp = execute_gql("queries/results.gql", self.client, variable_values=vargs)
            results = resp["dataLakeQuery"]
            rows.extend([edge["node"] for edge in results["results"]["edges"]])
        return results["status"], results["message"], rows

        