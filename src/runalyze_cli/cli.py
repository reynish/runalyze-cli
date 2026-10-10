#!/usr/bin/env python3
import base64
import json
import sys
from functools import wraps
from typing import List, Optional

import typer

from runalyze_cli.client import RunalyzeAPIError, RunalyzeClient
from runalyze_cli.utils import load_token, parse_props

app = typer.Typer()
activity_app = typer.Typer()
metrics_app = typer.Typer()
equipment_app = typer.Typer()
raceresult_app = typer.Typer()
settings_app = typer.Typer()
tag_app = typer.Typer()
stats_app = typer.Typer()
disease_app = typer.Typer()

app.add_typer(activity_app, name="activity", help="Activities")
app.add_typer(metrics_app, name="metrics", help="Health metrics")
app.add_typer(equipment_app, name="equipment", help="Equipment")
app.add_typer(raceresult_app, name="raceresult", help="Race results")
app.add_typer(settings_app, name="settings", help="Settings")
app.add_typer(tag_app, name="tag", help="Tags")
app.add_typer(stats_app, name="statistics", help="Statistics")
app.add_typer(disease_app, name="disease", help="Health: Disease and pain levels")
metrics_app.add_typer(
    disease_app, name="disease", help="Health: Disease and pain levels"
)


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
def activity_get(
    id: str,
    trackdata: bool = typer.Option(
        False, "--trackdata", help="Provide raw data for gps, heart rate and pace/speed"
    ),
):
    client = get_client()
    res = client.get_activity(id, trackdata=trackdata)
    print(json.dumps(res))


@activity_app.command("export")
@handle_api_errors
def activity_export(
    id: str,
    format: str = typer.Argument(
        ..., help="Format (csv, fit, fit-original, fitlog, gpx, kml, tcx)"
    ),
):
    client = get_client()
    res = client.export_activity(id, format)
    if isinstance(res, bytes):
        try:
            # Try to decode as UTF-8 (for GPX/TCX/KML/CSV)
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


@activity_app.command("share-image")
@handle_api_errors
def activity_share_image(
    id: str,
    format: str = typer.Argument(
        ..., help="Image format for social image (portrait, square)"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", help="Output file path to save binary image"
    ),
):
    client = get_client()
    res = client.get_activity_share_image(id, format)
    if output:
        with open(output, "wb") as f:
            f.write(res)
        print(json.dumps({"format": format, "output": output}))
    else:
        print(
            json.dumps(
                {
                    "format": format,
                    "content": base64.b64encode(res).decode("utf-8"),
                    "encoding": "base64",
                }
            )
        )


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
        help="Metric type (bloodGlucose, bloodPressure, bodyComposition, bodyTemperature, dailyNote, disease, heartRateMax, heartRateRest, hrv, menstrualCycle, mental, sleep)",
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


@metrics_app.command("bulk-upload")
@handle_api_errors
def metrics_bulk_upload(
    file: Optional[str] = typer.Option(
        None, "--file", help="Path to JSON file containing bulk health metrics"
    ),
    props: List[str] = typer.Argument(None),
):
    client = get_client()
    if file:
        with open(file, "r") as f:
            data = json.load(f)
    else:
        data = parse_props(props)
    res = client.bulk_upload_metrics(data)
    print(json.dumps(res))


@metrics_app.command("bulk-import")
@handle_api_errors
def metrics_bulk_import(
    file: Optional[str] = typer.Option(
        None, "--file", help="Path to JSON file containing bulk health metrics"
    ),
    props: List[str] = typer.Argument(None),
):
    return metrics_bulk_upload(file=file, props=props)


@metrics_app.command("forecast")
@handle_api_errors
def metrics_forecast():
    client = get_client()
    res = client.get_menstrual_cycle_forecast()
    print(json.dumps(res))


@metrics_app.command("menstrual-cycle-forecast")
@handle_api_errors
def metrics_menstrual_cycle_forecast():
    return metrics_forecast()


@metrics_app.command("latest")
@handle_api_errors
def metrics_latest_subcmd():
    client = get_client()
    res = client.get_latest_metrics()
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


@equipment_app.command("create")
@handle_api_errors
def equipment_create(props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.create_equipment(parse_props(props))
    print(json.dumps(res))


@equipment_app.command("update")
@handle_api_errors
def equipment_update(id: str, props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.update_equipment(id, parse_props(props))
    print(json.dumps(res))


@equipment_app.command("delete")
@handle_api_errors
def equipment_delete(id: str):
    client = get_client()
    res = client.delete_equipment(id)
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


@equipment_app.command("category-create")
@handle_api_errors
def equipment_category_create(props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.create_equipment_category(parse_props(props))
    print(json.dumps(res))


@equipment_app.command("category-update")
@handle_api_errors
def equipment_category_update(id: str, props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.update_equipment_category(id, parse_props(props))
    print(json.dumps(res))


@equipment_app.command("category-delete")
@handle_api_errors
def equipment_category_delete(id: str):
    client = get_client()
    res = client.delete_equipment_category(id)
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


@settings_app.command("date-range-create")
@handle_api_errors
def settings_date_range_create(props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.create_settings_date_range(parse_props(props))
    print(json.dumps(res))


@settings_app.command("date-range-update")
@handle_api_errors
def settings_date_range_update(id: str, props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.update_settings_date_range(id, parse_props(props))
    print(json.dumps(res))


@settings_app.command("date-range-delete")
@handle_api_errors
def settings_date_range_delete(id: str):
    client = get_client()
    res = client.delete_settings_date_range(id)
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


@stats_app.command("prognosis")
@handle_api_errors
def stats_prognosis():
    client = get_client()
    res = client.get_race_prognosis()
    print(json.dumps(res))


@disease_app.command("list")
@handle_api_errors
def disease_list(
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_diseases(limit=limit)
    print(json.dumps(res))


@disease_app.command("get")
@handle_api_errors
def disease_get(id: str):
    client = get_client()
    res = client.get_disease(id)
    print(json.dumps(res))


@disease_app.command("create")
@handle_api_errors
def disease_create(props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.create_disease(parse_props(props))
    print(json.dumps(res))


@disease_app.command("pain-level-list")
@handle_api_errors
def disease_pain_level_list(
    disease_id: str,
    limit: Optional[int] = typer.Option(
        None, help="Limit the number of results returned"
    ),
):
    client = get_client()
    res = client.get_disease_pain_levels(disease_id, limit=limit)
    print(json.dumps(res))


@disease_app.command("pain-level-get")
@handle_api_errors
def disease_pain_level_get(disease_id: str, pain_level_id: str):
    client = get_client()
    res = client.get_disease_pain_level(disease_id, pain_level_id)
    print(json.dumps(res))


@disease_app.command("pain-level-create")
@handle_api_errors
def disease_pain_level_create(disease_id: str, props: List[str] = typer.Argument(None)):
    client = get_client()
    res = client.create_disease_pain_level(disease_id, parse_props(props))
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
