"""Utility functions for use internally throughout the package.

Functions:
    validate_timestamp
"""

from datetime import datetime
from pathlib import Path
import re
import requests
from gql import gql, Client
from gql.transport.exceptions import TransportQueryError
import pytz

from .exceptions import EntityNotFoundError, AccessDeniedError

# This variable defines the root of the package on the filesystem, and allows us to import files
#   from within the package.
PACKAGE_ROOT = Path(__file__).parent.absolute()

# -- Regex Patterns
UUID_REGEX = re.compile(
    r"[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}"
)
EMAIL_REGEX = re.compile(r"[\w\-\.]+@([\w-]+\.)+[\w-]{2,4}")

IAM_ARN_REGEX = re.compile(r"arn:aws:iam::\d{12}:role\/[\w+=,.@\/-]{1,128}")
KMS_ARN_REGEX = re.compile(
    r"arn:aws:kms:[a-z]+-[a-z]+-\d:\d{12}:key\/[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}"  # pylint: disable=line-too-long
)  # pylint: disable=line-too-long

S3_BUCKET_NAME_REGEX = re.compile(r"[a-z\d][a-z\d.-]{1,61}[a-z\d]")

# For source, see https://docs.snowflake.com/en/sql-reference/identifiers-syntax
SNOWFLAKE_IDENTIFIER_UNQUOTED_REGEX = re.compile(r"[a-zA-Z_][\w\$\.]*")

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
    "us-gov-west-1",
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
    raise TypeError(
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


class RestInterfaceBase:
    """A base class for any interfaced using the Panther REST API."""

    # pylint: disable=too-few-public-methods
    #   Since this is a baseclass, and the subclassess will have more methods defined, this warning
    #   isn't helpful.

    def __init__(self, root_client, default_timeout: int = 30):
        """Initializes the Interface class.

        Args:
            root_client (Panther): the root Panther client.
            default_timeout (int, optional): the default length of time to wait for an API call to
                complete, before terminating the request
        """
        self.root = root_client
        self.default_timeout = default_timeout

    def _send_request(self, method: str, endpoint: str, body: dict = None, timeout=None):
        """A generic send-request function, that has centralized logic for formtatting the
        headers and adding timeouts.

        Args:
            method (str): which HTTP method to use - one of 'get', 'post', 'delete', or 'put'
            endpoint (str): the rest resource to send the request to
                examples: data_models, rules/My.Rule
            body (dict, optional): the request body, such as a rule specification
            timeout (int, optional): how long to wait for a response before aborting
                If unspecified, the default value passed to __init__ is used.
        """
        # Create the headers
        headers = {
            "X-API-Key": self.root.token,
        }

        # Send the request
        url = f"https://api.{self.root.domain}/v1/{endpoint}"
        timeout = timeout | self.root.default_timeout
        match method.lower().strip():
            case "get":
                return requests.get(url, headers=headers, timeout=timeout)
            case "post":
                return requests.post(url, data=body, headers=headers, timeout=timeout)
            case "put":
                return requests.post(url, data=body, headers=headers, timeout=timeout)
            case "delete":
                return requests.delete(url, headers=headers, timeout=timeout)


class GraphInterfaceBase:
    """A base class for any interfaces which use a GraphQL backend."""

    # pylint: disable=too-few-public-methods
    #   Since this is a baseclass, and the subclassess will have more methods defined, this warning
    #   isn't helpful.
    def __init__(self, root_client, gql_client: Client = None):
        """Initializes the Interface class.

        Args:
            root_client (Panther): the root Panther client.
            gql_client (gql.Client): the GQL client to use for queries. If not specified, defaults
                to the root_client's GQL client.
        """
        self.root = root_client
        # It's useful to be able to specify a different client for testing purposes. Normally, I
        #   wouldn't include an testing-only parameter as an init parameter, but since this class
        #   should never be instantiated by an end user, it's okay.
        # When we execute GQL. we'll check ig this is None, and if so, we'll fallback to the root
        #   GQL client.
        self.client = gql_client

    def execute_gql(self, fname: str, vargs: dict = None) -> dict:
        """Extracts a gql query from a file, and executes it on the given client with the supplied
        input, if any. Also does some common error handling.

        Args:
            fname (str): The name of the gql file to load the query template from.
            vargs (dict, optional): A dictionary with input arguments for the API call.
        """
        if vargs is None:
            vargs = {}
        query = gql_from_file(fname)
        try:
            client = self.client
            if client is None:
                client = self.root._gql()  # pylint: disable=protected-access
            return client.execute(query, variable_values=vargs)
        except TransportQueryError as e:
            for err in e.errors:
                msg = err.get("message", "")
                if msg.endswith("does not exist") or msg.endswith("not found"):
                    raise EntityNotFoundError(msg) from e
                if msg == "access denied":
                    method_name = err.get("path", ["<UNKNWON_METHOD>"])[-1]
                    raise AccessDeniedError(
                        f"API Token is not permitted to call method {method_name}"
                    ) from e
            # If we didn't catch the error above, raise the initial error
            raise


def convert_series_with_breakdown(series: list) -> dict:
    """Converts a SeriesWithBreakdown result into a version more compatible with plotting
    tools like Matplotlib. We extract the timestamps from the breakdown and make them a
    separate field, and then make an array of count values for each labelled item in the
    series. The intention is to make it easy to do things like plot info alerts over time:
        plot(results["timestamps"], results["INFO"])
    """
    # -- Validate Input
    # This is an internal-only function, so we'll skip the basic type checks and whatnot.
    #   The main worry I have is that the timestamp breakdowns will be different for each
    #   entry in the series... let's make sure they're the same.
    marker = "_".join(series[0]["breakdown"].keys())
    for item in series:
        assert "_".join(item["breakdown"].keys()) == marker

    data = {}
    data["timestamps"] = []
    for timestamp in marker.split("_"):
        data["timestamps"].append(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))
    # Extract Severity counts
    for item in series:
        data[item["label"]] = list(item["breakdown"].values())

    return data
