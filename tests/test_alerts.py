import pytest
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

@pytest.mark.parametrize(("alertid", "body", "fmt"), [
    ("c73bcdcc-2669-4bf6-81d3-e4an73fb11fd", "", "PLAIN_TEXT"),
    ("c73bcdcc26694bf681d3e4an73fb11fd", "", "PLAIN_TEXT"),
    ("definitely-not-a-uuid", "", "PLAIN_TEXT"),
    ("c73bcdcc26694bf681d3e4ae73fb11fd", 0, "PLAIN_TEXT"),
    ("c73bcdcc26694bf681d3e4ae73fb11fd", "", "NOT_A VALID_FORMAT"),
])
def test_get_alert_invalid_input(alertid, body, fmt):
    alerts = panther_seim.alerts.AlertsInterface(None)
    with pytest.raises(ValueError):
        alerts.add_comment(alertid, body, fmt)