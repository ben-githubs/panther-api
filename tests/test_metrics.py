import itertools
from datetime import datetime

import pytest
from pytz import timezone
from panther_seim.metrics import MetricsInterface

sample_series_with_breakown = [
    {
        "label": "Label1",
        "value": 13.0,
        "breakdown": {
            "2023-11-11T00:00:00Z": 11.0,
            "2023-11-11T03:00:00Z": 2.0
        }
    }, {
        "label": "Label2",
        "value": 3.0,
        "breakdown": {
            "2023-11-11T00:00:00Z": 1.0,
            "2023-11-11T03:00:00Z": 2.0
        }
    }
]
sample_series = [
    {
        "label": "label1",
        "value": 1.0,
    }, {
        "label": "label2",
        "value": 2.0
    }
]

class FakeClient:
    def execute(self, *args, **kwargs):
        return {
           "metrics": {
               "alertsPerRule": [
                   {
                       "entityId": "ID",
                       "label": "Label",
                       "value": "Value"
                   }
               ],
               "alertsPerSeverity": sample_series_with_breakown,
               "bytesIngestedPerSource": sample_series,
               "bytesProcessedPerSource": sample_series_with_breakown,
               "bytesQueriedPerSource": sample_series_with_breakown,
               "eventsProcessedPerLogType": sample_series_with_breakown,
               "latencyPerLogType": sample_series,
               "totalAlerts": 10.0,
               "totalBytesIngested": 10.0,
               "totalBytesProcessed": 10.0,
               "totalBytesQueried": 10.0,
               "totalEventsProcessed": 10.0
           } 
        }

metrics = MetricsInterface(None, FakeClient())

func_wo_interval = (
    metrics.alerts_count,
    metrics.alerts_per_rule,
    metrics.bytes_queried,
    metrics.bytes_processed,
    metrics.latency_per_logtype
)

func_w_interval = {
    metrics.events_processed_per_logtype,
    metrics.alerts_per_severity,
    metrics.all,
    metrics.bytes_processed_per_logtype,
    metrics.bytes_queried_per_logtype
}

invalid_timestamps_type = (
    None,
    1.1,
    [],
    {}
)

invalid_interval_type = (
    None,
    1.1,
    "",
    [],
    {}
)

invalid_timestamps_value = (
    -10,
    "Sunday, March 11, 2022",
    "2023-11-21",
)

invalid_interval_value = (
    0,
    -10
)

valid_timestamps_value = (
    1703774263,
    "2023-11-11T11:11:11Z",
    datetime(2023, 11, 11, 0, 0),
    datetime(2023, 11, 11, 0, 0, tzinfo=timezone("US/Central"))
)

valid_interval_value = (
    180,
    200
)

@pytest.mark.parametrize(
    ("func", "t1", "t2"),
    itertools.product(func_wo_interval, invalid_timestamps_type, invalid_timestamps_type)
)
def test_wo_interval_invalid_type(func, t1, t2):
    with pytest.raises(TypeError):
        func(t1, t2)

@pytest.mark.parametrize(
    ("func", "t1", "t2", "interval"),
    itertools.product(func_w_interval, invalid_timestamps_type, invalid_timestamps_type, invalid_interval_type)
)
def test_w_interval_invalid_type(func, t1, t2, interval):
    with pytest.raises(TypeError):
        func(t1, t2, interval)

@pytest.mark.parametrize(
    ("func", "t1", "t2"),
    itertools.product(func_wo_interval, invalid_timestamps_value, invalid_timestamps_value)
)
def test_wo_interval_invalid_value(func, t1, t2):
    with pytest.raises(ValueError):
        func(t1, t2)

@pytest.mark.parametrize(
    ("func", "t1", "t2", "interval"),
    itertools.product(func_w_interval, invalid_timestamps_value, invalid_timestamps_value, invalid_interval_value)
)
def test_w_interval_invalid_value(func, t1, t2, interval):
    with pytest.raises(ValueError):
        func(t1, t2, interval)

@pytest.mark.parametrize(
    ("func", "t1", "t2"),
    itertools.product(func_wo_interval, valid_timestamps_value, valid_timestamps_value)
)
def test_wo_interval_valid_value(func, t1, t2):
    func(t1, t2)

@pytest.mark.parametrize(
    ("func", "t1", "t2", "interval"),
    itertools.product(func_w_interval, valid_timestamps_value, valid_timestamps_value, valid_interval_value)
)
def test_w_interval_valid_value(func, t1, t2, interval):
    func(t1, t2, interval)