""" This module has the exceptions that will be raised elsewhere in the package.
"""


class PantherError(BaseException):
    """Base exception for all errors related to this package."""


class EntityNotFoundError(PantherError):
    """Raised when an entity requested by ID does not exist."""


class AccessDeniedError(PantherError):
    """Raised when a token has insufficient permissions to use an API method."""


class EntityAlreadyExistsError(PantherError):
    """Raised when the user tries to create an entity, but it already exists in Panther."""
