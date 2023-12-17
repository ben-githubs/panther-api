"""Provides a client for Panther's API. Panther is a SEIM platform.

Classes:
    Panther
"""

from __future__ import annotations
import typing
import re

import gql
from gql.transport.aiohttp import AIOHTTPTransport


# pylint: disable=too-few-public-methods
class Panther:
    """A client object for interacting with Panther's public API."""

    def __init__(self, token: str, domain: str) -> typing.Self:
        """Constructs the Panther client object.

        Args:
            token (str):  Your Panther API token.
            domain (str): Your Panther domain. ex: yourcompany.runpanther.net
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

    def _gql(self):
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
            self._gql_client = gql.Client(transport=transport, fetch_schema_from_transport=True)
