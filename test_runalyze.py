import json
import os
import sys
import base64
from unittest.mock import patch, MagicMock, mock_open
import pytest
import responses

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typer.testing import CliRunner
from utils import parse_props, load_token
from client import RunalyzeClient, RunalyzeAPIError
from runalyze import app

runner = CliRunner()

@pytest.mark.parametrize("props,expected", [
    (["a=1", "b=2"], {"a": 1, "b": 2}),
    (["a=\"str\"", "b=true"], {"a": "str", "b": True}),
    (["a=invalid_json"], {"a": "invalid_json"}),
    (["key="], {"key": ""}),
    (["=value"], {}),
    (["key=value=extra"], {"key": "value=extra"}),
    (["a=[1,2,3]", "b={\"nested\": \"val\"}"], {"a": [1, 2, 3], "b": {"nested": "val"}}),
    (["key=null"], {"key": None}),
    ([" "], {}),
    (["key= "], {"key": " "}),
    ([], {}),
    (None, {}),
])
def test_parse_props(props, expected):
    assert parse_props(props) == expected

def test_load_token_from_env_file():
    with patch("os.path.exists", return_value=True):
        m = mock_open(read_data="RUNALYZE_AUTH_TOKEN=test_token\n")
        with patch("builtins.open", m):
            assert load_token() == "test_token"

def test_load_token_from_env_var():
    with patch("os.path.exists", return_value=False):
        with patch("os.getenv", return_value="env_token"):
            assert load_token() == "env_token"

@responses.activate
def test_client_request_success():
    client = RunalyzeClient("test_token")
    responses.add(
        responses.GET,
        "https://runalyze.com/api/v1/test",
        json={"status": "ok"},
        status=200
    )
    res = client.request("GET", "/api/v1/test")
    assert res == {"status": "ok"}
    assert responses.calls[0].request.headers["token"] == "test_token"

@responses.activate
def test_client_request_204():
    client = RunalyzeClient("test_token")
    responses.add(
        responses.GET,
        "https://runalyze.com/api/v1/test",
        status=204
    )
    res = client.request("GET", "/api/v1/test")
    assert res == {"status": "success"}

@responses.activate
def test_client_request_http_error():
    client = RunalyzeClient("test_token")
    responses.add(
        responses.GET,
        "https://runalyze.com/api/v1/test",
        body="Error details",
        status=400
    )
    with pytest.raises(RunalyzeAPIError) as excinfo:
        client.request("GET", "/api/v1/test")
    assert "400 Client Error" in str(excinfo.value)
    assert "Error details" in str(excinfo.value)

def test_client_init_no_token():
    with pytest.raises(RunalyzeAPIError) as excinfo:
        RunalyzeClient(None)
    assert "RUNALYZE_AUTH_TOKEN not found" in str(excinfo.value)

# Client unit tests
@responses.activate
def test_client_get_activities():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/activity", json={"hydra:member": []}, status=200)
    assert client.get_activities() == []

@responses.activate
def test_client_get_activity():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/activity/1", json={"id": 1}, status=200)
    assert client.get_activity(1) == {"id": 1}

@responses.activate
def test_client_export_activity():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/activity/1/fit", body=b"fit", status=200)
    assert client.export_activity(1, "fit") == b"fit"

@responses.activate
def test_client_upload_activity():
    client = RunalyzeClient("token")
    responses.add(responses.POST, "https://runalyze.com/api/v1/activities/uploads", json={"id": "up"}, status=201)
    assert client.upload_activity(b"data") == {"id": "up"}

@responses.activate
def test_client_get_upload_status():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/activities/uploads/up", json={"status": "ok"}, status=200)
    assert client.get_upload_status("up") == {"status": "ok"}

@responses.activate
def test_client_metrics_methods():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/metrics/hrv", json={"hydra:member": []}, status=200)
    assert client.get_metrics("hrv") == []
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/metrics/hrv/1", json={"id": 1}, status=200)
    assert client.get_metric("hrv", 1) == {"id": 1}
    
    responses.add(responses.POST, "https://runalyze.com/api/v1/metrics/hrv", json={"id": 2}, status=201)
    assert client.create_metric("hrv", {"v": 1}) == {"id": 2}
    
    responses.add(responses.DELETE, "https://runalyze.com/api/v1/metrics/hrv/1", status=204)
    assert client.delete_metric("hrv", 1) == {"status": "success"}
    
    responses.add(responses.PATCH, "https://runalyze.com/api/v1/metrics/hrv/1", json={"id": 1}, status=200)
    assert client.update_metric("hrv", 1, {"v": 2}) == {"id": 1}
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/metrics/latest", json={}, status=200)
    assert client.get_latest_metrics() == {}

@responses.activate
def test_client_equipment_methods():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/equipment", json={"hydra:member": []}, status=200)
    assert client.get_equipment() == []
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/equipment/1", json={"id": 1}, status=200)
    assert client.get_equipment_item(1) == {"id": 1}
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/equipment/category", json={"hydra:member": []}, status=200)
    assert client.get_equipment_categories() == []
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/equipment/category/1", json={"id": 1}, status=200)
    assert client.get_equipment_category(1) == {"id": 1}
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/equipment/category/1/equipment", json={"hydra:member": []}, status=200)
    assert client.get_equipment_by_category(1) == []

@responses.activate
def test_client_services_and_sync():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/my/services", json=[], status=200)
    assert client.get_services() == []
    
    responses.add(responses.POST, "https://runalyze.com/api/v1/sync/changes", json={"status": "ok"}, status=200)
    assert client.sync_changes({}) == {"status": "ok"}

@responses.activate
def test_client_raceresult_methods():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/raceresult", json={"hydra:member": []}, status=200)
    assert client.get_race_results() == []
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/raceresult/1", json={"id": 1}, status=200)
    assert client.get_race_result(1) == {"id": 1}
    
    responses.add(responses.DELETE, "https://runalyze.com/api/v1/raceresult/1", status=204)
    assert client.delete_race_result(1) == {"status": "success"}
    
    responses.add(responses.PATCH, "https://runalyze.com/api/v1/raceresult/1", json={"id": 1}, status=200)
    assert client.update_race_result(1, {}) == {"id": 1}

@responses.activate
def test_client_settings_and_tags():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/settings/date-range", json={"hydra:member": []}, status=200)
    assert client.get_settings_date_ranges() == []
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/settings/date-range/1", json={"id": 1}, status=200)
    assert client.get_settings_date_range(1) == {"id": 1}
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/tag", json={"hydra:member": []}, status=200)
    assert client.get_tags() == []
    
    responses.add(responses.GET, "https://runalyze.com/api/v1/tag/1", json={"id": 1}, status=200)
    assert client.get_tag(1) == {"id": 1}

@responses.activate
def test_client_statistics():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/statistics/current", json={}, status=200)
    assert client.get_current_statistics() == {}

@responses.activate
def test_client_pagination_relative():
    client = RunalyzeClient("token")
    responses.add(
        responses.GET, 
        "https://runalyze.com/api/v1/list", 
        json={"hydra:member": [{"id": 1}], "hydra:view": {"hydra:next": "/api/v1/list?page=2"}}, 
        status=200
    )
    responses.add(
        responses.GET, 
        "https://runalyze.com/api/v1/list?page=2", 
        json={"hydra:member": [{"id": 2}]}, 
        status=200
    )
    assert client.request("GET", "/api/v1/list", paginate=True) == [{"id": 1}, {"id": 2}]

@responses.activate
def test_client_pagination_fallback_list():
    client = RunalyzeClient("token")
    responses.add(responses.GET, "https://runalyze.com/api/v1/list", json=[{"id": 1}], status=200)
    assert client.request("GET", "/api/v1/list", paginate=True) == [{"id": 1}]

# CLI Tests
@patch("runalyze.get_client")
def test_cli_activity_list(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_activities.return_value = [{"id": 1, "title": "Run"}]
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["activity", "list"])
    assert result.exit_code == 0
    assert "Run" in result.stdout
    mock_client.get_activities.assert_called_once()

@patch("runalyze.get_client")
def test_cli_activity_get(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_activity.return_value = {"id": 1}
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["activity", "get", "1"])
    assert result.exit_code == 0
    assert "\"id\": 1" in result.stdout

@patch("runalyze.get_client")
def test_cli_activity_upload(mock_get_client):
    mock_client = MagicMock()
    mock_client.upload_activity.return_value = {"id": "up123"}
    mock_get_client.return_value = mock_client
    
    with patch("builtins.open", mock_open(read_data=b"data")):
        result = runner.invoke(app, ["activity", "upload", "file.fit"])
    
    assert result.exit_code == 0
    assert "up123" in result.stdout

@patch("runalyze.get_client")
def test_cli_activity_upload_status(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_upload_status.return_value = {"status": "processed"}
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["activity", "upload-status", "up123"])
    assert result.exit_code == 0
    assert "processed" in result.stdout

@patch("runalyze.get_client")
def test_cli_metrics_list(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_metrics.return_value = []
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["metrics", "list", "hrv"])
    assert result.exit_code == 0
    mock_client.get_metrics.assert_called_with("hrv", limit=None)

@patch("runalyze.get_client")
def test_cli_metrics_create(mock_get_client):
    mock_client = MagicMock()
    mock_client.create_metric.return_value = {"status": "created"}
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["metrics", "create", "heartRateRest", "value=60"])
    assert result.exit_code == 0
    assert "created" in result.stdout
    mock_client.create_metric.assert_called_with("heartRateRest", {"value": 60})

@patch("runalyze.get_client")
def test_cli_metrics_delete(mock_get_client):
    mock_client = MagicMock()
    mock_client.delete_metric.return_value = {"status": "deleted"}
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["metrics", "delete", "hrv", "1"])
    assert result.exit_code == 0
    assert "deleted" in result.stdout

@patch("runalyze.get_client")
def test_cli_metrics_update(mock_get_client):
    mock_client = MagicMock()
    mock_client.update_metric.return_value = {"status": "updated"}
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["metrics", "update", "hrv", "1", "value=100"])
    assert result.exit_code == 0
    assert "updated" in result.stdout

@patch("runalyze.get_client")
def test_cli_metrics_latest(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_latest_metrics.return_value = {}
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["metrics-latest"])
    assert result.exit_code == 0

@patch("runalyze.get_client")
def test_cli_equipment_list(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_equipment.return_value = []
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["equipment", "list"])
    assert result.exit_code == 0

@patch("runalyze.get_client")
def test_cli_services(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_services.return_value = []
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["services"])
    assert result.exit_code == 0

@patch("runalyze.get_client")
def test_cli_sync_changes(mock_get_client):
    mock_client = MagicMock()
    mock_client.sync_changes.return_value = {"status": "synced"}
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["sync-changes", "a=1"])
    assert result.exit_code == 0

@patch("runalyze.get_client")
def test_cli_raceresult_list(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_race_results.return_value = []
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["raceresult", "list"])
    assert result.exit_code == 0

@patch("runalyze.get_client")
def test_cli_settings_date_range(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_settings_date_ranges.return_value = []
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["settings", "date-range"])
    assert result.exit_code == 0

@patch("runalyze.get_client")
def test_cli_tag_list(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_tags.return_value = []
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["tag", "list"])
    assert result.exit_code == 0

@patch("runalyze.get_client")
def test_cli_statistics_current(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_current_statistics.return_value = {}
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["statistics", "current"])
    assert result.exit_code == 0

@responses.activate
def test_client_pagination_hydra():
    client = RunalyzeClient("test_token")
    # Page 1
    responses.add(
        responses.GET,
        "https://runalyze.com/api/v1/list",
        json={
            "hydra:member": [{"id": 1}],
            "hydra:view": {"hydra:next": "https://runalyze.com/api/v1/list?page=2"},
        },
        status=200
    )
    # Page 2
    responses.add(
        responses.GET,
        "https://runalyze.com/api/v1/list?page=2",
        json={
            "hydra:member": [{"id": 2}],
        },
        status=200
    )
    
    res = client.request("GET", "/api/v1/list", paginate=True)
    assert res == [{"id": 1}, {"id": 2}]
    assert len(responses.calls) == 2

@responses.activate
def test_client_rate_limiting_retry():
    client = RunalyzeClient("test_token")
    # First call: 429
    responses.add(
        responses.GET,
        "https://runalyze.com/api/v1/test",
        status=429
    )
    # Second call: 200
    responses.add(
        responses.GET,
        "https://runalyze.com/api/v1/test",
        json={"status": "ok"},
        status=200
    )
    
    res = client.request("GET", "/api/v1/test")
    assert res == {"status": "ok"}
    assert len(responses.calls) == 2

@patch("runalyze.get_client")
def test_cli_error_handling(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_activities.side_effect = RunalyzeAPIError("API Error")
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["activity", "list"])
    assert result.exit_code == 1
    assert "Error: API Error" in result.output

@responses.activate
def test_client_binary_response():
    client = RunalyzeClient("test_token")
    responses.add(
        responses.GET,
        "https://runalyze.com/api/v1/export",
        body=b"FITDATA",
        content_type="application/octet-stream",
        status=200
    )
    res = client.request("GET", "/api/v1/export")
    assert res == b"FITDATA"

@patch("runalyze.get_client")
def test_cli_activity_export_binary(mock_get_client):
    mock_client = MagicMock()
    mock_client.export_activity.return_value = b"\xde\xad\xbe\xef" # Binary
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["activity", "export", "1", "fit"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["format"] == "fit"
    assert data["encoding"] == "base64"
    assert base64.b64decode(data["content"]) == b"\xde\xad\xbe\xef"

@patch("runalyze.get_client")
def test_cli_activity_export_text(mock_get_client):
    mock_client = MagicMock()
    mock_client.export_activity.return_value = b"<gpx></gpx>" # Text in bytes
    mock_get_client.return_value = mock_client
    
    result = runner.invoke(app, ["activity", "export", "1", "gpx"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["format"] == "gpx"
    assert data["content"] == "<gpx></gpx>"
    assert "encoding" not in data
