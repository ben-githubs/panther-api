""" Code for interacting with alerts is specified here.
"""
from collections import defaultdict
from datetime import datetime
import typing
import gql
from ._util import validate_timestamp, gql_from_file, UUID_REGEX, EMAIL_REGEX

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
            has_more = results["alerts"].get("pageInfo", {}).get("hasNextPage")
            cursor = results["alerts"].get("pageInfo", {}).get("endCursor")

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
        if not UUID_REGEX.fullmatch(alertid):
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
        if not UUID_REGEX.fullmatch(alertid):
            raise ValueError(f"ID value {alertid} is not a UUID.")
        if not isinstance(body, str):
            raise ValueError(f"Comment body must be a string, not {type(body).__name__}.")
        if not isinstance(format, str):
            raise ValueError(f"Format spec must be a string, not {type(format).__name__}.")
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
    
    def update(
            self,
            alertids: typing.List[str] | str,
            status: str = None,
            assignee: str = None
        ) -> dict:
        """ Make changes to the status or assignee of an alert.

        Args:
            alertids (str, list): The ID(s) of the alert to update.
                Can be a string to update a single alert, or a list to bulk update many alerts.
            status (str): The new status of the alert. Optional.
                Must be one of "CLOSED", "OPEM", "RESOLVED", or "TRIAGED".
            assignee (str): The ID or email of the new assignee. Optional.
        
        Returns:
            The update data of each alert affected.
        """

        # -- Validate and Transform input
        if not any([isinstance(alertids, type) for type in (str, list)]):
            raise ValueError(
                f"Alert ID input must be either a list or a str, not '{type(alertids).__name__}'."
            )
        if isinstance(alertids, str): # If this is a single alert ID
            alertids = [alertids]
        # Validate regex
        for alertid in alertids:
            if not UUID_REGEX.fullmatch(alertid):
                raise ValueError(f"ID value {alertid} is not a UUID.")
        
        if status:
            if not isinstance(status, str):
                raise ValueError(f"New alert status must be a string, not {type(status).__name__}.")
            # Convert to uppercase
            status = status.upper()
            if status not in ("OPEN", "TRIAGED", "CLOSED", "RESOLVED"):
                raise ValueError(f"Invalid status: {status}")

        if assignee and not isinstance(assignee, str):
            raise ValueError(
                f"New alert assignee must be a string, not {type(assignee).__name__}."
            )
        
        # -- Update Alert(s)
        # Panther's backend has 2 API endpoints for alert updates; the status and assignee are 
        #   updated separately. We're combining both commands into 1 in this library to align
        #   more closely with CRUDL.
        alerts = defaultdict(dict)
        if assignee:
            # Could be an email, could be an ID
            if EMAIL_REGEX.fullmatch(assignee):
                query = gql_from_file("alerts/update_assignee_by_email.gql")
                results = self.client.execute(query, variable_values = {
                    "input": {
                        "ids": alertids,
                        "assigneeEmail": assignee
                    }
                })
                for result in results["updateAlertsAssigneeByEmail"]["alerts"]:
                    alerts[result['id']].update(result)
            else:
                query = gql_from_file("alerts/update_assignee_by_id.gql")
                results = self.client.execute(query, variable_values = {
                    "input": {
                        "ids": alertids,
                        "assigneeId": assignee
                    }
                })
                for result in results["updateAlertsAssigneeById"]["alerts"]:
                    alerts[result['id']].update(result)
        if status:
            query = gql_from_file("alerts/update_status.gql")
            results = self.client.execute(query, variable_values = {
                "input": {
                    "ids": alertids,
                    "status": status
                }
            })
            for result in results["updateAlertStatusById"]["alerts"]:
                print(result)
                alerts[result['id']].update(result)
        
        if len(alerts) == 1:
            return list(alerts.values())[0]
        return list(alerts.values())

