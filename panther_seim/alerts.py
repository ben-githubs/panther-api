""" Code for interacting with alerts is specified here.
"""
from datetime import datetime
import re
import gql
from ._util import validate_timestamp, gql_from_file

UUID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}"
)

class AlertsInterface:
    """An interface for working with alerts in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def __init__(self, client: gql.Client):
        self.client = client

    def list(
        self, start: str | int | datetime, end: str | int | datetime = datetime.utcnow()
    ) -> list[dict]:
        """Lists all alerts which were created within the given timespan.

        Args:
            start (str, int, datetime): the start of the timeframe to search
            end (str, int, datetime): the end of the timeframe to search. If not provided, we
                fetch all alerts created between 'start' and now.

        Returns:
            A list of all alerts created wthin the timespan.
        """
        # Validate and convert timestamps
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        query = gql_from_file("alerts/list.gql")

        all_alerts = []
        has_more = True
        cursor = None

        while has_more:
            results = self.client.execute(
                query,
                variable_values={
                    "input": {"createdAtBefore": end, "createdAtAfter": start, "cursor": cursor}
                },
            )
            all_alerts.extend([edge["node"] for edge in results["alerts"]["edges"]])
            has_more = results["alerts"]["pageInfo"]["hasNextPage"]
            cursor = results["alerts"]["pageInfo"]["endCursor"]

        return all_alerts

    def get(self, alertid: str) -> dict:
        """Returns a single alert.

        Args:
            id (str): the ID of the alert to return.

        Returns:
            The alert with the specied ID, or None if no alert exists with that ID.
        """

        # Validate input
        if not isinstance(alertid, str):
            raise ValueError(f"ID must be a string, not {type(alertid).__name__}.")
        if not UUID_PATTERN.fullmatch(alertid):
            raise ValueError(f"ID value {alertid} is not a UUID.")

        # Get Alert
        query = gql_from_file("alerts/get.gql")
        result = self.client.execute(query, variable_values={"id": alertid})
        return result.get("alert")


    def add_comment(self, alertid: str, body: str, format: str = "PLAIN_TEXT") -> dict:
        """ Adds a comment to an existing alert.

        Args:
            alertid (str): the ID of the alert to comment on.
            body (str): the content of the comment.
            format (str): the formatting of 'body'. Allowed values are 'PLAIN_TEXT' and 'HTML'.
                If format is 'HTML', you can use HTML tags in your 'body' to add formatting to your
                alert comment.
        
        Returns:
            Details about the created comment.
        """
        # Validate the input
        if not isinstance(alertid, str):
            raise ValueError(f"Alert ID must be a string, not {type(alertid).__name__}.")
        if not UUID_PATTERN.fullmatch(alertid):
            raise ValueError(f"ID value {alertid} is not a UUID.")
        if not isinstance(body, str):
            raise ValueError(f"Comment body must be a string, not {type(alertid).__name__}.")
        if not isinstance(format, str):
            raise ValueError(f"Format spec must be a string, not {type(alertid).__name__}.")
        format = format.upper()
        if format not in ("PLAIN_TEXT", "HTML"):
            raise ValueError(f"Format must be one of 'PLAIN_TEXT', 'HTML'; got '{format}'.")
        
        # Invoke API
        query = gql_from_file("alerts/add_comment.gql")
        result = self.client.execute(query, variable_values = {
            "input": {
                "alertId": alertid,
                "body": body,
                "format": format
            }
        })
        return result.get("createAlertComment")