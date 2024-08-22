""" This module has the exceptions that will be raised elsewhere in the package.
"""

from typing import List

from .rule_test_results import TestResult


class PantherError(BaseException):
    """Base exception for all errors related to this package."""


class EntityNotFoundError(PantherError):
    """Raised when an entity requested by ID does not exist."""


class AccessDeniedError(PantherError):
    """Raised when a token has insufficient permissions to use an API method."""


class EntityAlreadyExistsError(PantherError):
    """Raised when the user tries to create an entity, but it already exists in Panther."""


class QueryCancelled(PantherError):
    """Raised when a datalake query has been cancelled by the user."""


class QueryError(PantherError):
    """Raised when a datalake query errored during execution."""


class RuleTestFailure(PantherError):
    """Raised when an API call requires rule tests to pass, but tests fail instead."""

    def __init__(self, message: str, results: List[TestResult]):
        """
        Initialize the exception,
        Args:
            message (str): The text of the error message
            results (list[TestResult]): Detailed results of each unit test, including errors
        """
        self.results = results
        super().__init__(message)
