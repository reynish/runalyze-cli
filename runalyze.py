#!/usr/bin/env python3
import base64
import json
import sys
import typer
from typing import Optional, List
from functools import wraps

from client import RunalyzeClient, RunalyzeAPIError
from utils import load_token, parse_props

app = typer.Typer()
activity_app = typer.Typer()
metrics_app = typer.Typer()
equipment_app = typer.Typer()
raceresult_app = typer.Typer()
settings_app = typer.Typer()
tag_app = typer.Typer()
stats_app = typer.Typer()

app.add_typer(activity_app, name="activity", help="Activities")
app.add_typer(metrics_app, name="metrics", help="Health metrics")
app.add_typer(equipment_app, name="equipment", help="Equipment")
app.add_typer(raceresult_app, name="raceresult", help="Race results")
app.add_typer(settings_app, name="settings", help="Settings")
app.add_typer(tag_app, name="tag", help="Tags")
app.add_typer(stats_app, name="statistics", help="Statistics")


def get_client():
    token = load_token()
    return RunalyzeClient(token)


def handle_api_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except RunalyzeAPIError as e:
            print(f"Error: {e}", file=sys.stderr)
            raise typer.Exit(code=1)

    return wrapper


@activity_app.command("list")
@handle_api_errors
def activity_list(
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_activities(limit=limit)
    print(json.dumps(res))


@activity_app.command("get")
@handle_api_errors
def activity_get(id: str):
    client = get_client()
    res = client.get_activity(id)
    print(json.dumps(res))


@activity_app.command("export")
@handle_api_errors
def activity_export(
    id: str,
    format: str = typer.Argument(
        ..., help="Format (fit, fit-original, fitlog, gpx, kml, tcx)"
    ),
):
    client = get_client()
    res = client.export_activity(id, format)
    if isinstance(res, bytes):
        try:
            # Try to decode as UTF-8 (for GPX/TCX/KML)
            content = res.decode("utf-8")
            print(json.dumps({"format": format, "content": content}))
        except UnicodeDecodeError:
            # Binary data (FIT)
            print(
                json.dumps(
                    {
                        "format": format,
                        "content": base64.b64encode(res).decode("utf-8"),
                        "encoding": "base64",
                    }
                )
            )
    else:
        print(json.dumps(res))


@activity_app.command("upload")
@handle_api_errors
def activity_upload(file: str):
    client = get_client()
    with open(file, "rb") as f:
        file_content = f.read()
    res = client.upload_activity(file_content)
    print(json.dumps(res))


@activity_app.command("upload-status")
@handle_api_errors
def activity_upload_status(id: str):
    client = get_client()
    res = client.get_upload_status(id)
    print(json.dumps(res))


@metrics_app.command("list")
@handle_api_errors
def metrics_list(
    metric: str = typer.Argument(
        ...,
        help="Metric type (bloodGlucose, bloodPressure, bodyComposition, bodyTemperature, dailyNote, heartRateMax, heartRateRest, hrv, mental, sleep)",
    ),
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_metrics(metric, limit=limit)
    print(json.dumps(res))


@metrics_app.command("get")
@handle_api_errors
def metrics_get(metric: str, id: str):
    client = get_client()
    res = client.get_metric(metric, id)
    print(json.dumps(res))


@metrics_app.command("create")
@handle_api_errors
def metrics_create(metric: str, props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.create_metric(metric, parse_props(props))
    print(json.dumps(res))


@metrics_app.command("delete")
@handle_api_errors
def metrics_delete(metric: str, id: str):
    client = get_client()
    res = client.delete_metric(metric, id)
    print(json.dumps(res))


@metrics_app.command("update")
@handle_api_errors
def metrics_update(metric: str, id: str, props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.update_metric(metric, id, parse_props(props))
    print(json.dumps(res))


@app.command("metrics-latest")
@handle_api_errors
def metrics_latest():
    client = get_client()
    res = client.get_latest_metrics()
    print(json.dumps(res))


@equipment_app.command("list")
@handle_api_errors
def equipment_list(
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_equipment(limit=limit)
    print(json.dumps(res))


@equipment_app.command("get")
@handle_api_errors
def equipment_get(id: str):
    client = get_client()
    res = client.get_equipment_item(id)
    print(json.dumps(res))


@equipment_app.command("categories")
@handle_api_errors
def equipment_categories(
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_equipment_categories(limit=limit)
    print(json.dumps(res))


@equipment_app.command("category")
@handle_api_errors
def equipment_category(id: str):
    client = get_client()
    res = client.get_equipment_category(id)
    print(json.dumps(res))


@equipment_app.command("category-equipment")
@handle_api_errors
def equipment_category_equipment(
    id: str,
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_equipment_by_category(id, limit=limit)
    print(json.dumps(res))


@app.command("services")
@handle_api_errors
def services():
    client = get_client()
    res = client.get_services()
    print(json.dumps(res))


@app.command("sync-changes")
@handle_api_errors
def sync_changes(props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.sync_changes(parse_props(props))
    print(json.dumps(res))


@raceresult_app.command("list")
@handle_api_errors
def raceresult_list(
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_race_results(limit=limit)
    print(json.dumps(res))


@raceresult_app.command("get")
@handle_api_errors
def raceresult_get(id: str):
    client = get_client()
    res = client.get_race_result(id)
    print(json.dumps(res))


@raceresult_app.command("delete")
@handle_api_errors
def raceresult_delete(id: str):
    client = get_client()
    res = client.delete_race_result(id)
    print(json.dumps(res))


@raceresult_app.command("update")
@handle_api_errors
def raceresult_update(id: str, props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.update_race_result(id, parse_props(props))
    print(json.dumps(res))


@settings_app.command("date-range")
@handle_api_errors
def settings_date_range(
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_settings_date_ranges(limit=limit)
    print(json.dumps(res))


@settings_app.command("date-range-get")
@handle_api_errors
def settings_date_range_get(id: str):
    client = get_client()
    res = client.get_settings_date_range(id)
    print(json.dumps(res))


@tag_app.command("list")
@handle_api_errors
def tag_list(
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_tags(limit=limit)
    print(json.dumps(res))


@tag_app.command("get")
@handle_api_errors
def tag_get(id: str):
    client = get_client()
    res = client.get_tag(id)
    print(json.dumps(res))


@stats_app.command("current")
@handle_api_errors
def stats_current():
    client = get_client()
    res = client.get_current_statistics()
    print(json.dumps(res))


def main():
    try:
        app()
    except RunalyzeAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
