""" Code for retrieving Panther metrics is specified here.
"""

from datetime import datetime

from ._util import GraphInterfaceBase, validate_timestamp

class MetricsInterface(GraphInterfaceBase):
    def all(
        self,
        start: str | int | datetime,
        end: str | int | datetime,
        interval: int = 180
    ) -> dict:
        """Retreives all available metrics for the time period.

        Args:
            start (str, datetime): The start of the period to fetch metrics for.
                When a string, it must be in ISO format. When an integer, it represents a Unix
                timestamp in UTC. When a string or datetime, if no timezone is specified, we assume
                UTC is intended.
            end (str, datetime): The end of the period to fetch metrics for.
                When a string, it must be in ISO format. When an integer, it represents a Unix
                timestamp in UTC. When a string or datetime, if no timezone is specified, we assume
                UTC is intended.
            interval (int, optional): The interval between metrics checks. Used in breakdowns.
        
        Returns:
            A dictionary with metrics on alerts, queries, and ingestion.
        """
        # -- Validate input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        if not isinstance(interval, int):
            raise TypeError(f"'interval' must be an integer; got {type(interval).__name__}.")
        if interval <= 0:
            raise ValueError("'interval' must be greater than zero.")

        # -- Invoke API
        vargs = {
            "input": {
                "fromDate": start,
                "toDate": end,
                "intervalInMinutes": interval
            }
        }
        return self.execute_gql("metrics/all.gql", vargs)
