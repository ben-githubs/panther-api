import pytest
from graphql import DocumentNode

from panther_seim.databases import DatabaseInterface

class FakeClient:
    def execute(self, query, variable_values = dict()):
        assert isinstance(query, DocumentNode)
        assert isinstance(variable_values, dict)

        return {
            "dataLakeDatabase": {
                "foo": "bar"
            }
        }

client = DatabaseInterface(None, FakeClient())

@pytest.mark.parametrize("dbase", [
    11, # not a string
    1.1, # not a string
    object(), # not a string
    list(), # not a string
])
def test_get_invalid_type(dbase):
    with pytest.raises(TypeError):
        client.get(dbase)

@pytest.mark.parametrize("dbase", [
    "@invalid_symbol",
    "this oen has spaces",
    "this-one-has-dashes",
    "0this_one_starts_with_a_digit",
])
def test_get_invalid_value(dbase):
    with pytest.raises(ValueError):
        client.get(dbase)

@pytest.mark.parametrize("dbase", [
    "panther_logs.public",
    "database.schema",
    "database",
    "dollarSymbolsAreAllowed$",
    "underscores_are_allowed"
])
def test_get_valid_input(dbase):
    client.get(dbase)