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
DateTimeScalar = GraphQLScalarType(
    name="DateTime", serialize=_util.validate_timestamp, parse_value=_util.parse_datetime
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
