""" This module has the exceptions that will be raised elsewhere in the package.
"""

class PantherError(BaseException):
    pass

class EntityNotFoundError(PantherError):
    """ Raised when an entity requested by ID does not exist.
    """
    pass