""" Code for retrieving Panther metrics is specified here.
"""

from datetime import datetime

from ._util import GraphInterfaceBase, validate_timestamp, convert_series_with_breakdown


class MetricsInterface(GraphInterfaceBase):
    """An interface for working with metrics in Panther. An instance of this class will be attached
    to the Panther client object.
    """

    def all(
        self, start: str | int | datetime, end: str | int | datetime, interval: int = 180
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
        vargs = {"input": {"fromDate": start, "toDate": end, "intervalInMinutes": interval}}
        return self.execute_gql("metrics/all.gql", vargs)["metrics"]

    def alerts_per_rule(
        self,
        start: str | int | datetime,
        end: str | int | datetime,
    ) -> dict:
        """Retreives a count of alerts, grouped by triggering rule, for the time period.

        Args:
            start (str, datetime): The start of the period to fetch metrics for.
                When a string, it must be in ISO format. When an integer, it represents a Unix
                timestamp in UTC. When a string or datetime, if no timezone is specified, we assume
                UTC is intended.
            end (str, datetime): The end of the period to fetch metrics for.
                When a string, it must be in ISO format. When an integer, it represents a Unix
                timestamp in UTC. When a string or datetime, if no timezone is specified, we assume
                UTC is intended.

        Returns:
            A dictionary with metrics on alerts, queries, and ingestion.
        """
        # -- Validate input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end}}
        results = self.execute_gql("metrics/alerts_per_rule.gql", vargs)
        data = {}
        for datum in results["metrics"]["alertsPerRule"]:
            data[datum["entityId"]] = {"count": datum["value"], "rule_description": datum["label"]}
        return data

    def alerts_per_severity(
        self, start: str | int | datetime, end: str | int | datetime, interval: int = 180
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
            A dictionary with metrics on alerts. The dictionary keys correspond to each severity,
            the values are a list fo timestamps, and the counts of alerts of each severity, binned
            according to the timestamp list.
        """
        # -- Validate input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        if not isinstance(interval, int):
            raise TypeError(f"'interval' must be an integer; got {type(interval).__name__}.")
        if interval <= 0:
            raise ValueError("'interval' must be greater than zero.")

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end, "intervalInMinutes": interval}}
        results_raw = self.execute_gql("metrics/alerts_by_severity.gql", vargs)
        results = results_raw["metrics"]["alertsPerSeverity"]

        return convert_series_with_breakdown(results)
