import pytest
from panther_seim._util import gql_from_file

@pytest.mark.parametrize("filename", [
    "alerts/list.gql",
    "alerts/get.gql",
    "alerts/add_comment.gql",
    "users/list.gql"
])
def test_gql_file(filename: str):
    gql_from_file(filename)