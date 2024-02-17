""" This module has code for converting some of the scalars returned by GQL queries into Python 
objects.
"""

from datetime import datetime, timezone as tz

from graphql import GraphQLScalarType
import gql
from gql.utilities import update_schema_scalars

from . import _util


async def update_schemas(client: gql.Client):
    """Queries the Panther backend and retrieves the graphql schemas for the client."""
    async with client as _:
        schema = client.schema
        update_schema_scalars(schema, [DateTimeScalar, TimestampScalar])


# -- Datetimes
def parse_datetime(value: str) -> datetime:
    """Converts a datetime string returned by Panther into a datetime object."""
    # Validate input
    if not isinstance(value, str):
        raise TypeError(f"Timestamp should be a string, but got '{type(value).__name__}'.")

    # Panther may return the timestamp with the no fractional seconds, or with fraction seconds
    #   of varying sig figs. Python only converts 0 or 6 sig figs, so we need to handle the
    #   variable input.
    converted = None
    parts = value.split(".")
    match len(parts):
        case 1:  # No fractional seconds
            converted = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        case 2:
            frac = parts[1][:-1]  # Remove the Z
            frac = frac.ljust(6, "0")[:6]  # Convert to 6 sig figs
            new_value = f"{parts[0]}.{frac}Z"
            converted = datetime.strptime(new_value, "%Y-%m-%dT%H:%M:%S.%fZ")

    return converted.replace(tzinfo=tz.utc)


DateTimeScalar = GraphQLScalarType(
    name="DateTime", serialize=_util.validate_timestamp, parse_value=parse_datetime
)


# -- Timestamps
def parse_timestamp(value: int) -> datetime:
    """Converts a unix timestamp into a datetime. Assumes UTC for timezone."""
    # Validate Input
    if not isinstance(value, int):
        raise TypeError(f"Timestamp should be an integer, but got '{type(value).__name__}'.")

    # Convert and Append Timezone
    return datetime.fromtimestamp(value, tz=tz.utc)


TimestampScalar = GraphQLScalarType(
    name="Timestamp", serialize=_util.validate_timestamp, parse_value=parse_timestamp
)
