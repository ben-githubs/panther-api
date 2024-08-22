""" Code for managing realtime (streaming) rules

Reference:
    https://docs.panther.com/panther-developer-workflows/api/rest/rules
"""

from dataclasses import dataclass, field
from enum import StrEnum
import json
from typing import Any, List

import yaml

from .exceptions import PantherError, EntityNotFoundError, EntityAlreadyExistsError, RuleTestFailure
from ._util import RestInterfaceBase, get_rest_response, deep_cast_time
from .rule_test_results import TestError, TestResult, TestDetectionRecordFunctions


class Severities(StrEnum):
    """Corresponds to the severity level of a raised alert."""

    INFO = "INFO"
    LOW = "LOW"
    MED = "MEDIUM"
    HIGH = "HIGH"
    CRIT = "CRITICAL"


@dataclass
class Mock:
    """Mock functions can be used to override python functions in unit tests."""

    object_name: str
    return_value: Any

    def to_dict(self) -> dict:
        """Returns this object as a dictionary, ready for use in the Rest API."""
        return {"objectName": self.object_name, "returnValue": self.return_value}


@dataclass
class UnitTest:
    """Unit tests ensure that a rule performs as-expected for a specific log event.

    Args:
        name (str): Name/ID of the unit test. Should be descriptive.
        expected_result (bool): Whether this event should trigger the rule and raise an alert.
        event (str, dict): Log event to pass to rule. If a string, must be in JSON format.
        mocks (list[dict], optional): List of function calls to mock when testing your rule.
            Mock dicts/objects can be created with rules.
    """

    name: str
    expected_result: bool
    event: str | dict
    mocks: List[dict | Mock] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Returns this object as a dictionary, ready for use in the Rest API."""
        return {
            "name": self.name,
            "expectedResult": self.expected_result,
            "resource": json.dumps(self.event),
            "mocks": self.mocks,
        }


def unpack_test_result(body: dict | str) -> TestResult:
    """Converts the test result dict returned by Panther's API into a class that can be easily
    accessed."""
    if isinstance(body, str):
        body = json.loads(body)

    result = TestResult(
        name=body.get("name"),
        passed=body.get("passed"),
        errored=body.get("errored"),
        trigger_alert=body.get("triggerAlert"),
    )
    if "error" in body:
        result.error = TestError(
            message=body["error"].get("message"), code=body["error"].get("code")
        )
    if "functions" in body:
        result.functions = TestDetectionRecordFunctions(
            alert_context=body["functions"].get("alertContext"),
            dedup=body["functions"].get("dedup"),
            description=body["functions"].get("description"),
            destinations=body["functions"].get("destinations"),
            reference=body["functions"].get("reference"),
            severity=body["functions"].get("severity"),
            title=body["functions"].get("title"),
        )
    return result


class RulesInterface(RestInterfaceBase):
    """An interface for working with realtime rules in Panther. An instance of this class will be
    attached to the Panther client object."""

    @staticmethod
    def _convert_timestamps(rule: dict):
        """Some fields of the rule object are timestamps, but are returned as strings. We cast
        them to datetime here."""
        if "createdAt" in rule:
            deep_cast_time(rule, "createdAt")
        if "lastModified" in rule:
            deep_cast_time(rule, "lastModified")
        return rule

    def list(self) -> List[dict]:
        """Lists all realtime rules that are configured in Panther.

        Returns:
            A list of realtime rules.
        """
        # Get Rules
        # pylint: disable=duplicate-code
        rules = []
        limit = 50
        has_more = True
        cursor = None

        while has_more:
            params = {"limit": limit}
            if cursor:
                params["cursor"] = cursor
            resp = self._send_request("get", "rules", params=params)
            results = get_rest_response(resp)
            cursor = results.get("next")
            has_more = cursor
            rules += results.get("results", [])

        # Timestamp conversion
        if self.root.auto_convert:
            rules = [RulesInterface._convert_timestamps(q) for q in rules]

        return rules

    def get(self, rule_id: str) -> dict:
        """Returns the rule with the provided ID.

        Args:
            rule_id (str): The ID of the rule to fetch
        """
        resp = self._send_request("get", f"rules/{rule_id}")
        match resp.status_code:
            case 200:
                rule = get_rest_response(resp)
                if self.root.auto_convert:
                    rule = RulesInterface._convert_timestamps(rule)
                return rule
            case 404:
                msg = f"No rule found with ID '{rule_id}'"
                raise EntityNotFoundError(msg)
            case _:
                # If none of the status codes above matched, then this is an unknown error.
                raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")

    @staticmethod
    def _create(  # pylint: disable=too-many-arguments, too-many-locals, too-many-branches
        rule_id: str,
        body: str,
        severity: Severities | str,
        dedup: int = None,
        desc: str = None,
        name: str = None,
        enabled: bool = None,
        inline_filters: str | List[dict] = None,
        log_types: List[str] = None,
        managed: bool = None,
        reports: dict = None,
        runbook: str = None,
        summary_attributes: List[str] = None,
        tags: List[str] = None,
        tests: List[dict | UnitTest] = None,
    ) -> dict:
        """Returns the base payload used in the create and update API requests."""

        payload = {"id": rule_id, "body": body, "severity": str(severity)}

        if dedup is not None:
            payload["dedupPeriodMinutes"] = dedup
        if desc is not None:
            payload["description"] = desc
        if name is not None:
            payload["displayName"] = name
        if enabled is not None:
            payload["enabled"] = enabled
        if inline_filters is not None:
            if not isinstance(inline_filters, str):
                payload["inlineFilters"] = yaml.dump(inline_filters)
            else:
                payload["inlineFilters"] = inline_filters
        if log_types is not None:
            payload["logTypes"] = log_types
        if managed is not None:
            payload["managed"] = managed
        if reports is not None:
            payload["reports"] = reports
        if runbook is not None:
            payload["runbook"] = runbook
        if summary_attributes is not None:
            payload["summaryAttributes"] = summary_attributes
        if tags is not None:
            payload["tags"] = tags
        if tests is not None:
            payload["tests"] = tests

        return payload

    def create(  # pylint: disable=too-many-arguments, too-many-locals
        self,
        rule_id: str,
        body: str,
        severity: Severities | str,
        log_types: List[str],
        dedup: int = None,
        desc: str = None,
        name: str = None,
        enabled: bool = None,
        inline_filters: str | List[dict] = None,
        managed: bool = None,
        reports: dict = None,
        runbook: str = None,
        summary_attributes: List[str] = None,
        tags: List[str] = None,
        tests: List[dict | UnitTest] = None,
        run_tests_first: bool = None,
        run_tests_only: bool = None,
    ) -> dict:
        """Create a new rule.

        Args:
            rule_id (str): The id of the rule
            body (str): The python body of the rule
            severity (str or Severity): The default severity of any raised alert
            log_types (list[str]): Which log types this rule will run against.
            dedup (int, optional): The amount of time, in minutes, for grouping alerts. Default: 60
            desc (str, optional): The description of the rule
            name (str, optional): The display name of the rule.
                If not specified, the RuleID will be displayed.
            enabled (bool, optional): Determines whether or not the rule is active
            inline_filters (str or list[dict], optional): The filters for the rule.
                If a string, must be a YAML representation of a list of filter objects. Filter
                objects are specified as dictionaries, and can be created with the
                rules.create_filter function.
            managed (bool, optional): Determines if a rule is managed by Panther. Default: False
            reports (dict, optional): Maps to report types, such as MITRE tactics
            summary_attributes (list[str], optional): A list of fields in the event to create top
                5 summaries for
            tags (list[str]): Tags for the rule
            tests (list[dict or UnitTest], optional): Unit tests for the rule.
            run_tests_first (bool, optional): Whether to run tests prior to saving. Default: True
            run_tests_only (bool, optional): Whether to run tests and not save. Default: False

        Returns:
            The created rule
        """
        # Build base payload
        payload = RulesInterface._create(
            rule_id,
            body,
            severity,
            dedup,
            desc,
            name,
            enabled,
            inline_filters,
            log_types,
            managed,
            reports,
            runbook,
            summary_attributes,
            tags,
            tests,
        )
        params = {}
        if run_tests_first is not None:
            params["run-test-first"] = run_tests_first
        if run_tests_only is not None:
            params["run-tests-only"] = run_tests_only

        # Invoke API
        resp = self._send_request("POST", "rules", body=payload, params=params)
        match resp.status_code:
            case 200:
                rule = get_rest_response(resp)
                if self.root.auto_convert:
                    rule = RulesInterface._convert_timestamps(rule)
                return rule
            case 204:  # No-content response
                # It's unclear in Panther's docs when this status code is returned, rather than 200
                return None
            case 400:
                # Check if the error is due to failing unit tests
                if "application/json" in resp.headers.get("Content-Type", ""):
                    err = resp.json()
                    if err["message"] == "you have failing tests":
                        test_names = []
                        for test in err["testResults"]:
                            if not test["passed"] or not test["errored"]:
                                test_names.append(test["name"])
                        raise RuleTestFailure(
                            f"Cannot upload rule {rule_id} due to failing unit tests: "
                            f"{', '.join(test_names)}",
                            results=[unpack_test_result(r) for r in err["testResults"]],
                        )
                # Otherwise, raise generic 400 error
                raise PantherError(f"Invalid request: {resp.text}")
            case 409:
                raise EntityAlreadyExistsError(
                    f"Cannot save rule; rule ID '{rule_id}' is already in use"
                )

    def update(  # pylint: disable=too-many-arguments, too-many-locals
        self,
        rule_id: str,
        body: str = None,
        severity: Severities | str = None,
        log_types: List[str] = None,
        dedup: int = None,
        desc: str = None,
        name: str = None,
        enabled: bool = None,
        inline_filters: str | List[dict] = None,
        managed: bool = None,
        reports: dict = None,
        runbook: str = None,
        summary_attributes: List[str] = None,
        tags: List[str] = None,
        tests: List[dict | UnitTest] = None,
        run_tests_first: bool = None,
        run_tests_only: bool = None,
    ) -> dict:
        """Creates a new rule, or updates an existing rule.

        Args:
            rule_id (str): The id of the rule to edit
            body (str, optional): The new python body of the rule
            severity (str or Severity): The default severity of any raised alert
            log_types (list[str]): Which log types this rule will run against.
            dedup (int, optional): The amount of time, in minutes, for grouping alerts. Default: 60
            desc (str, optional): The description of the rule
            name (str, optional): The display name of the rule.
                If not specified, the RuleID will be displayed.
            enabled (bool, optional): Determines whether or not the rule is active
            inline_filters (str or list[dict], optional): The filters for the rule.
                If a string, must be a YAML representation of a list of filter objects. Filter
                objects are specified as dictionaries, and can be created with the
                rules.create_filter function.
            managed (bool, optional): Determines if a rule is managed by Panther. Default: False
            reports (dict, optional): Maps to report types, such as MITRE tactics
            summary_attributes (list[str], optional): A list of fields in the event to create top
                5 summaries for
            tags (list[str]): Tags for the rule
            tests (list[dict or UnitTest], optional): Unit tests for the rule.
            run_tests_first (bool, optional): Whether to run tests prior to saving. Default: True
            run_tests_only (bool, optional): Whether to run tests and not save. Default: False
        """
        # Get the current version of the rule
        # NOTE: This implementation is different from other update functions in this module. There
        #   is no "create if not exists" functionality here. If you try to update a rule that
        #   doesn't already exist, you will get errors. (This is despite the REST framework
        #   allowing rule creation via PUT.)
        current_rule = self.get(rule_id)

        # Create a dict containing the updates requested
        changes = RulesInterface._create(
            rule_id,
            body,
            severity,
            dedup,
            desc,
            name,
            enabled,
            inline_filters,
            log_types,
            managed,
            reports,
            runbook,
            summary_attributes,
            tags,
            tests,
        )

        # Create the API payload by combining the original rule with our changes
        payload = current_rule | changes

        # Invoke API Call
        params = {"run_tests_first": run_tests_first, "run_tests_only": run_tests_only}
        resp = self._send_request("PUT", f"rules/{rule_id}", body=payload, params=params)
        # Handle returns codes. We shouldn't ever get a 201, since we require the rule already
        #   exist when calling self.get(rule_id) above.
        match resp.status_code:
            case 200:
                return get_rest_response(resp)
            case 204:
                return None
            case 400:
                # Check if the error is due to failing unit tests
                if "application/json" in resp.headers.get("Content-Type", ""):
                    err = resp.json()
                    if err["message"] == "you have failing tests":
                        test_names = []
                        for test in err["testResults"]:
                            if not test["passed"] or not test["errored"]:
                                test_names.append(test["name"])
                        raise RuleTestFailure(
                            f"Cannot upload rule {rule_id} due to failing unit tests: "
                            f"{', '.join(test_names)}",
                            results=[unpack_test_result(r) for r in err["testResults"]],
                        )
                # Otherwise, raise generic 400 error
                raise PantherError(f"Invalid request: {resp.text}")
            case _:
                raise PantherError(f"Unexpected response with code {resp.code}: {resp.text}")

    def delete(self, rule_id, ignore404: bool = False) -> None:
        """Deletes a rule.

        Args:
            rule_id (str): The ID of the rule to delete
            ignore404 (bool, optional): whether to raise an error if the rule doesn't exist
                Set to True to suppress an EntityNotFoundError
        """
        resp = self._send_request("DELETE", f"rules/{rule_id}")

        # pylint: disable=duplicate-code
        match resp.status_code:
            case 204:
                return
            case 400:
                raise PantherError(f"Invalid request: {resp.text}")
            case 404:
                if not ignore404:
                    raise EntityNotFoundError(
                        f"Cannot delete rule with ID {rule_id}; ID does not exist"
                    )
                return
            case _:
                # If none of the status codes above matched, then this is an unknown error.
                raise PantherError(f"Unknown error with code {resp.status_code}: {resp.text}")
