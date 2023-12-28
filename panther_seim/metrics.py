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
        """All available metrics for the time period.

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
        """Number of alerts generated over the time period, segmented by source detection.

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
        """Number of alerts generated over the time period, segmented by severity.

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

    def alerts_count(
        self,
        start: str | int | datetime,
        end: str | int | datetime,
    ) -> int:
        """Total number of alerts generated within the time period.

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
            The number of alerts generated.
        """
        # -- Validate input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end}}
        results = self.execute_gql("metrics/alerts_count.gql", vargs)
        return int(results["metrics"]["totalAlerts"])

    def bytes_processed(
        self,
        start: str | int | datetime,
        end: str | int | datetime,
    ) -> int:
        """Volume of logs ingested over the time frame.

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
            The number of bytes ingested.
        """
        # -- Validate input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end}}
        results = self.execute_gql("metrics/bytes_processed.gql", vargs)
        return int(results["metrics"]["totalBytesProcessed"])

    # Note: the Panther-API name for this metric is 'BytesProcessedPerSource'. However, that name
    #   is misleading, and sounds like it returns the bytes processed by a specific log source.
    #   To avoid confusion, we label this metric as 'bytes_processed_per_logtype', which is what it
    #   actually represents.
    def bytes_processed_per_logtype(
        self, start: str | int | datetime, end: str | int | datetime, interval: int = 180
    ) -> dict:
        """Volume of logs ingested over the time frame, segmented by log type.

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
            A dictionary with metrics on log processing. The dictionary has the following structure:
                timestasmps (list[datetime]): A list of datetimes, which represent the beginning of
                    each interval.
                $log_type (list[int]): A list of the number of bytes processed for $log_type. Each
                    item in the list is the volume processed in the corresponding interval in the
                    'timestamps' list.
        """
        # -- Validate Input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        if not isinstance(interval, int):
            raise TypeError(f"'interval' must be an integer; got {type(interval).__name__}.")
        if interval <= 0:
            raise ValueError("'interval' must be greater than zero.")

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end, "intervalInMinutes": interval}}
        results_raw = self.execute_gql("metrics/bytes_processed_log_type.gql", vargs)
        results = results_raw["metrics"]["bytesProcessedPerSource"]

        return convert_series_with_breakdown(results)

    def bytes_queried(
        self,
        start: str | int | datetime,
        end: str | int | datetime,
    ) -> int:
        """Volume of logs queried over the time frame.

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
            The number of bytes queried.
        """
        # -- Validate input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end}}
        results = self.execute_gql("metrics/bytes_queried.gql", vargs)
        return int(results["metrics"]["totalBytesQueried"])

    # Note: the Panther-API name for this metric is 'BytesQueriedPerSource'. However, that name is
    #   misleading, and sounds like it returns the bytes queried from a specific log source. To
    #   avoid confusion, we label this metric as 'bytes_queried_per_logtype', which is what it
    #   actually represents.
    def bytes_queried_per_logtype(
        self, start: str | int | datetime, end: str | int | datetime, interval: int = 180
    ) -> dict:
        """Breakdown of the volume of logs queried over the timespan, segmented by log type.

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
            A dictionary with metrics on log queries. The dictionary has the following structure:
                timestasmps (list[datetime]): A list of datetimes, which represent the beginning of
                    each interval.
                $log_type (list[int]): A list of the number of bytes queried for $log_type. Each
                    item in the list is the volume of data queried in the corresponding interval in
                    the 'timestamps' list.
        """
        # -- Validate Input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        if not isinstance(interval, int):
            raise TypeError(f"'interval' must be an integer; got {type(interval).__name__}.")
        if interval <= 0:
            raise ValueError("'interval' must be greater than zero.")

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end, "intervalInMinutes": interval}}
        results_raw = self.execute_gql("metrics/bytes_queried_log_type.gql", vargs)
        results = results_raw["metrics"]["bytesQueriedPerSource"]

        return convert_series_with_breakdown(results)

    def events_processed_per_logtype(
        self, start: str | int | datetime, end: str | int | datetime, interval: int = 180
    ) -> dict[str, list]:
        """Breakdown of the number of log events ingested, segmented by log type.

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
            A dictionary with metrics on event ingestion. The dict has the following structure:
                timestasmps (list[datetime]): A list of datetimes, which represent the beginning of
                    each interval.
                $log_type (list[int]): A list of the number of events ingested for $log_type. Each
                    item in the list is the volume of data ingested in the corresponding interval in
                    the 'timestamps' list.
        """
        # -- Validate Input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        if not isinstance(interval, int):
            raise TypeError(f"'interval' must be an integer; got {type(interval).__name__}.")
        if interval <= 0:
            raise ValueError("'interval' must be greater than zero.")

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end, "intervalInMinutes": interval}}
        results_raw = self.execute_gql("metrics/events_processed_log_type.gql", vargs)
        results = results_raw["metrics"]["eventsProcessedPerLogType"]

        return convert_series_with_breakdown(results)

    def latency_per_logtype(
        self,
        start: str | int | datetime,
        end: str | int | datetime,
    ) -> dict:
        """Average log latency over the time period, segmented by log type.

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
            A dictionary that represents the latency breakdown. The dictionary keys are the names
            of each log type, and the values are the average log latency, in seconds.
        """
        # -- Validate Input
        start = validate_timestamp(start)
        end = validate_timestamp(end)

        # -- Invoke API
        vargs = {"input": {"fromDate": start, "toDate": end}}
        results_raw = self.execute_gql("metrics/latency_log_type.gql", vargs)
        results = results_raw["metrics"]["latencyPerLogType"]

        # -- Format output
        # The data from the backend is a list of dictionaries, with 2 fields: one for the log type
        #   name, and one for the latency. To make it easier to extract info, we reformat this data
        #   into a single dictionary, where the keys are the log type name, and the values are the
        #   latency.
        data = {}
        for item in results:
            data[item["label"]] = item["value"]

        return data
