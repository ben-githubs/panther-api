""" Small module to define some dataclasses we use elsewhere in the application. """

from dataclasses import dataclass


@dataclass
class TestError:
    """Contains information about a unit test error."""

    message: str
    code: str | None = None


@dataclass
class TestDetectionSubRecord:
    """Describes the result of a rule function."""

    output: str
    error: TestError | None = None


@dataclass
class TestDetectionRecordFunctions:  # pylint: disable=too-many-instance-attributes
    """Contains information on a rule's aux function. Returned in TestResult."""

    alert_context: TestDetectionSubRecord | None = None
    dedup: TestDetectionSubRecord | None = None
    description: TestDetectionSubRecord | None = None
    destinations: TestDetectionSubRecord | None = None
    reference: TestDetectionSubRecord | None = None
    runbook: TestDetectionSubRecord | None = None
    severity: TestDetectionSubRecord | None = None
    title: TestDetectionSubRecord | None = None


@dataclass
class TestResult:
    """Contains information about a unit test result."""

    name: str
    passed: bool
    errored: bool
    trigger_alert: bool
    error: TestError | None = None
    functions: None = None
