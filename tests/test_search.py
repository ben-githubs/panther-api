import os

import pytest
from graphql import DocumentNode
from dotenv import load_dotenv

from panther_seim import Panther
from panther_seim.search import SearchInterface
from panther_seim.exceptions import QueryError

load_dotenv(".env")

class TestExecute:
    client = Panther(
        token = os.environ.get("PANTHER_API_TOKEN"),
        domain = os.environ.get("PANTHER_API_DOMAIN")
    )

    @pytest.mark.parametrize("sql", [
        10, # int
        1.1, # float
        None, # NoneType
        [''], # list
        ('',), # tuple,
        {'foo': 'bar'}, # dict
        {'foo', 'bar'}, # set
    ])
    def test_invalid_type(self, sql):
        with pytest.raises(TypeError):
            self.client.search.execute_async(sql)
    
    @pytest.mark.skipif(os.environ.get("TEST_LIVE") is None, reason="Live testing is not enabled.")
    @pytest.mark.parametrize("sql", [
        "SELECT * FROM fake table",
        "SELECT * FROM panther_views.public.all_rule_matches WHERE not_a_real_func"
    ])
    def test_invalid_sql(self, sql):
        with pytest.raises(QueryError):
            self.client.search.execute(sql)
    

    @pytest.mark.skipif(os.environ.get("TEST_LIVE") is None, reason="Live testing is not enabled.")
    @pytest.mark.parametrize("sql", [
        "SELECT 10",
        "SELECT * FROM panther_monitor.public.data_audit ORDER BY p_event_time desc LIMIT 10"
    ])
    def test_valid_sql_live(self, sql):
        assert self.client.search.execute(sql, refresh=1) is not None

class TestResult:
    class FakeClient:
        def execute(self, query, variable_values = dict()):
            assert isinstance(query, DocumentNode)
            assert isinstance(variable_values, dict)

            return {
                "dataLakeQuery": {
                    "status": "test_case",
                    "message": "this is a test case"
                }
            }
        
    client = SearchInterface(None, FakeClient())

    @pytest.mark.parametrize("queryid", [
        10, # int
        1.1, # float
        None, # NoneType
        [''], # list
        ('',), # tuple,
        {'foo': 'bar'}, # dict
        {'foo', 'bar'}, # set
    ])
    def test_invalid_type(self, queryid):
        with pytest.raises(TypeError):
            self.client.results(queryid)
    
    @pytest.mark.parametrize("queryid", [
        "c73bcdcc-2669-4bf6-81d3-e4an73fb11fd",
        "c73bcdcc26694bf681d3e4an73fb11fd",
        "definitely-not-a-uuid"
    ])
    def test_invalid_value(self, queryid):
        with pytest.raises(ValueError):
            self.client.results(queryid)
    
    @pytest.mark.parametrize("queryid", [
        "c73bcdcc-2669-4bf6-81d3-e4ae73fb11fd"
    ])
    def test_valid_value(self, queryid):
        self.client.results(queryid)