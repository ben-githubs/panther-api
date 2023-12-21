""" Code for interacting with alerts is specified here.
"""

from typing import List

import gql
from ._util import SNOWFLAKE_IDENTIFIER_UNQUOTED_REGEX, execute_gql


class DatabaseInterface:
    """An interface for working with databases in Panther. An instance of this class will be
    attached to the Panther client object.
    """

    def __init__(self, client: gql.Client):
        self.client = client

    def list(self) -> List[dict]:
        """Lists all available databases, and details their tables and columns..

        Returns:
            A list of all datalake objects.
        """

        # -- Invoke API
        result = execute_gql("databases/list.gql", self.client)
        return result["dataLakeDatabases"]

    def get(self, database: str) -> dict:
        """Lists all available database tables, and describes their columns.

        Args:
            database (str): The name of a panther database.

        Returns:
            A a description of the database, and a list of tables and columns contained therein.
        """

        # -- Validate Input
        if not isinstance(database, str):
            raise TypeError(
                f"Parameter 'database' must be a string; got '{type(database).__name__}'."
            )
        # Check if the database name is valid. We're validating based on the unquoted
        #   identifier rules, because Panther's API doesn't work for quoted database names,
        #   at least as far as I know.
        if not SNOWFLAKE_IDENTIFIER_UNQUOTED_REGEX.fullmatch(database):
            raise ValueError(f"Invalid database name: {database}")

        # -- Invoke API
        queryfile = "databases/get.gql"
        vargs = {"database": database}  # Variable Values
        result = execute_gql(queryfile, self.client, variable_values=vargs)
        return result["dataLakeDatabase"]
