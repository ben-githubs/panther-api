"""Provides a client for Panther's API. Panther is a SEIM platform.

Classes:
    Panther
"""

from __future__ import annotations
import typing
import re
import asyncio

import gql
from gql.transport.aiohttp import AIOHTTPTransport

from .alerts import AlertsInterface
from .cloud_accounts import CloudAccountsInterface
from .databases import DatabaseInterface
from .queries import QueriesInterface
from .users import UsersInterface

from .gql_scalars import update_schemas


# pylint: disable=too-few-public-methods, too-many-instance-attributes
class Panther:
    """A client object for interacting with Panther's public API."""

    def __init__(self, token: str, domain: str, auto_convert: bool = False) -> typing.Self:
        """Constructs the Panther client object.

        Args:
            token (str):  Your Panther API token.
            domain (str): Your Panther domain. ex: yourcompany.runpanther.net
            auto_convert (bool) = False: If true, we will convert some values from the backend
                into Python objects. For example, timestamp strings will be converted to datetime
                objects. This setting makes working with the reslt set in Python more convenient,
                but may cause trouble when serializing API results into JSON or other formats.
        """
        # Validate input
        if not isinstance(token, str):
            raise ValueError(f"Token must be of type 'str', not '{type(token).__name__}")
        if not isinstance(domain, str):
            raise ValueError(f"Domain must be of type 'str', not '{type(domain).__name__}")
        domain_pattern = r"[a-z][a-z0-9\-\.]+[a-z0-9]"
        if not re.fullmatch(domain_pattern, domain):
            raise ValueError(
                (
                    f"Invalid domain '{domain}'. Ensure the domain is valid, and doesn't include "
                    "the transport schema (https, http). Examples of valid domains are "
                    "'acme.runpanther.net', 'panther.secops.acme.com', etc."
                )
            )

        self.token, self.domain = token, domain
        self.auto_convert = auto_convert

        self.alerts = AlertsInterface(self._gql())
        self.cloud_accounts = CloudAccountsInterface(self._gql())
        self.databases = DatabaseInterface(self._gql())
        self.queries = QueriesInterface(self._gql())
        self.users = UsersInterface(self._gql())

    def _gql(self) -> gql.Client:
        """Lazily loads a GQL client and returns it. Used internally for makign GQL API calls to
        Panther.

        Returns:
            The Panther client objects own client for makign GQL API calls.
        """
        # pylint: disable=attribute-defined-outside-init
        try:
            self._gql_client
        except AttributeError:
            transport = AIOHTTPTransport(
                url=f"https://api.{self.domain}/public/graphql", headers={"X-API-KEY": self.token}
            )
            self._gql_client = gql.Client(
                transport=transport,
                fetch_schema_from_transport=True,
                parse_results=self.auto_convert,
            )

            if self.auto_convert:
                asyncio.run(update_schemas(self._gql_client))

        return self._gql_client
