"""Utility functions for use internally throughout the package.

Functions:
    validate_timestamp
"""

from datetime import datetime
from pathlib import Path
import re
from gql import gql, Client
from gql.transport.exceptions import TransportQueryError
import pytz

from .exceptions import EntityNotFoundError, AccessDeniedError
# This variable defines the root of the package on the filesystem, and allows us to import files
#   from within the package.
PACKAGE_ROOT = Path(__file__).parent.absolute()

# Regex Patterns
UUID_REGEX = re.compile(
    r"[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}"
)
EMAIL_REGEX = re.compile(r"[\w\-\.]+@([\w-]+\.)+[\w-]{2,4}")

ARN_REGEX = re.compile(r"arn:aws:iam::\d{12}:role\/[\w+=,.@\/-]{1,128}")

# AWS Regions
AWS_REGIONS = {
    "us-east-2",
    "us-east-1",
    "us-west-1",
    "us-west-2",
    "af-south-1",
    "ap-east-1",
    "ap-south-2",
    "ap-southeast-3",
    "ap-southeast-4",
    "ap-south-1",
    "ap-northeast-3",
    "ap-northeast-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-northeast-1",
    "ca-central-1",
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-south-1",
    "eu-west-3",
    "eu-south-2",
    "eu-north-1",
    "eu-central-2",
    "il-central-1",
    "me-south-1",
    "me-central-1",
    "sa-east-1",
    "us-gov-east-1",
    "us-gov-west-1"
}


# Panther is really weird. Some entites, like alerts, can only be referenced by IDs in hexadecimal
#   format (without dashes), while others, like cloud accounts, require the dashes to be present.
#   In an attempt at user friendliness, we allow end users to specify IDs in either format, and use
#   these functions to automatically transform to the Panther-required format.
def to_uuid(val: str) -> str:
    """Converts a pure hexadecimal ID (without dashes) into a UUID format ID (with dashes).

    Args:
        val (str): the ID to transform to UUID format.

    Returns:
        the same ID, formatted with dashes.
    """
    if not UUID_REGEX.fullmatch(val):
        raise ValueError(f"Invalid ID: {val}")
    if "-" not in val:
        val = "-".join([val[0:8], val[8:12], val[12:16], val[16:20], val[20:]])
    return val


def to_hex(val: str) -> str:
    """Converts a UUID-style ID (with dashes) into a pure hexadecima format ID (without dashes).

    Args:
        val (str): the ID to transform to hexadecimal format.

    Returns:
        the same ID, formatted without dashes.
    """
    if not UUID_REGEX.fullmatch(val):
        raise ValueError(f"Invalid ID: {val}")
    return val.replace("-", "")


def execute_gql(queryfile: str, client: Client, variable_values: dict = {}) -> dict:
    """ Extracts a gql query from a file, and executes it on the given client with the supplied
    input, if any. Also does some common error handling.
    """
    query = gql_from_file(queryfile)
    try:
        return client.execute(query, variable_values=variable_values)
    except TransportQueryError as e:
        for err in e.errors:
            msg = err.get("message", "")
            if msg.endswith("does not exist"):
                raise EntityNotFoundError(msg) from e
            elif msg == "access denied":
                method_name = e.get("path", ["<UNKNWON_METHOD>"])[-1]
                raise AccessDeniedError(f"API Token is not permitted to call method {method_name}")
        # If we didn't catch the error above, raise the initial error
        raise


def validate_timestamp(timestamp: int | str | datetime):
    """We allow all timestamps to be specified as integers (representing UNIX epoch time, strings
    (in ISO 8601 format), or as datetime objects. If a naive datetime object is passed, we assume
    it's intended as UTC. In this function, we validate that the input value is a timestamp, and
    convert to a string which we can use for raw API calls to Panther.

    Args:
        timestamp (int, str, or datetime): The input timestamp to be validated and converted.
    """
    if isinstance(timestamp, int):
        # UNIX timestamps must be greater than zero.
        if timestamp <= 0:
            raise ValueError(
                "Invalid timestamp 'timestamp' - UNIX timestamps must be greater than zero."
            )
        # Conver to a timestamp, which we can then convert into a string in the next step.
        timestamp = datetime.fromtimestamp(timestamp)
    if isinstance(timestamp, datetime):
        # If there's a timezone attached, then convert it to UTC
        if timestamp.tzinfo is not None and timestamp.tzinfo.utcoffset(timestamp) is not None:
            timestamp = timestamp.astimezone(pytz.utc)
        # Otherwise, assume the passed timestamp is intended as UTC
        else:
            timestamp = timestamp.replace(tzinfo=pytz.utc)
        # Convert to ISO 8601 format
        return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(timestamp, str):
        # Assert that the timestamp string is the correct format. If there's an error, we let it
        #   propogate upwards.
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        # If we didn't error out in the above step, return the string as-is.
        return timestamp
    # If we get here, then the input is none of the allowed value types, so we should return an
    #   error.
    raise ValueError(
        (
            "Invalid timestamp - timestamp must be a string, integer, or datetime object, "
            f"not {type(timestamp).__name__}."
        )
    )


def gql_from_file(path: str | Path):
    """Returns a gql query object based on the contents of a file. Because it is preferable to
    have GQL query templates in their own files (rather than hard-coded into the package as
    strings), we need to make it easy to extract the queries from those files and convert them to
    gql objects.

    Args:
        path (str, pathlib.Path): the path to the .gql file, relative to the project root.
    """
    # Convert to path, if not already
    if not isinstance(path, Path):
        path = Path(path)

        # Assert that the file is a .gql file
        if path.suffix != ".gql":
            raise ValueError(f"Path {path} does not point to a gql file.")

    # Make path relative to root
    path = PACKAGE_ROOT / "gql_templates" / path

    # Get the file contents
    contents = ""
    with path.open("r") as f:
        contents = f.read()

    # Create a new GQL query from the file contents, and return it
    return gql(contents)
