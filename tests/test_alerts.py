import pytest
import gql
import panther_seim.alerts

@pytest.mark.parametrize("alertid", [
    "c73bcdcc-2669-4bf6-81d3-e4an73fb11fd",
    "c73bcdcc26694bf681d3e4an73fb11fd",
    "definitely-not-a-uuid"
])
def test_get_alert_invalid_input(alertid):
    alerts = panther_seim.alerts.AlertsInterface(None)
    with pytest.raises(ValueError):
        alerts.get(alertid)