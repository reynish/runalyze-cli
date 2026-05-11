#!/usr/bin/env python3
import argparse
import json
import os
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

def load_token():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.startswith("RUNALYZE_AUTH_TOKEN="):
                    return line.split("=", 1)[1].strip()
    return os.getenv("RUNALYZE_AUTH_TOKEN")

TOKEN = load_token()
BASE_URL = "https://runalyze.com"

def make_request(path, method="GET", data=None, headers=None):
    if not TOKEN:
        print("Error: RUNALYZE_AUTH_TOKEN not found.", file=sys.stderr)
        sys.exit(1)

    url = BASE_URL + path
    req_headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)

    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = Request(url, data=req_data, headers=req_headers, method=method)

    try:
        with urlopen(req) as response:
            if response.status == 204:
                return {"status": "success"}
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        print(f"Error: {e.code} {e.reason}", file=sys.stderr)
        try:
            print(e.read().decode("utf-8"), file=sys.stderr)
        except:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def parse_props(props):
    data = {}
    if not props:
        return data
    for prop in props:
        if "=" in prop:
            k, v = prop.split("=", 1)
            try:
                data[k] = json.loads(v)
            except json.JSONDecodeError:
                data[k] = v
    return data

def main():
    parser = argparse.ArgumentParser(description="Runalyze CLI")
    subparsers = parser.add_subparsers(dest="resource", required=True)

    # Activity
    p_activity = subparsers.add_parser("activity", help="Activities")
    sp_activity = p_activity.add_subparsers(dest="action", required=True)
    sp_activity.add_parser("list", help="List activities")
    p_act_get = sp_activity.add_parser("get", help="Get activity")
    p_act_get.add_argument("id", help="Activity ID")
    
    p_act_export = sp_activity.add_parser("export", help="Export activity")
    p_act_export.add_argument("id", help="Activity ID")
    p_act_export.add_argument("format", choices=["fit", "fit-original", "fitlog", "gpx", "kml"], help="Format")

    p_act_upload = sp_activity.add_parser("upload", help="Upload activity")
    p_act_upload.add_argument("file", help="Path to file")

    p_act_upload_status = sp_activity.add_parser("upload-status", help="Get upload status")
    p_act_upload_status.add_argument("id", help="Upload ID")

    # Metrics
    p_metrics = subparsers.add_parser("metrics", help="Health metrics")
    p_metrics.add_argument("metric", choices=[
        "bloodGlucose", "bloodPressure", "bodyComposition", 
        "bodyTemperature", "dailyNote", "heartRateMax", 
        "heartRateRest", "hrv", "mental", "sleep"
    ], help="Metric type")
    sp_metrics = p_metrics.add_subparsers(dest="action", required=True)
    
    sp_metrics.add_parser("list", help="List metric values")
    
    p_met_get = sp_metrics.add_parser("get", help="Get metric value")
    p_met_get.add_argument("id", help="Metric ID")
    
    p_met_create = sp_metrics.add_parser("create", help="Create metric value")
    p_met_create.add_argument("props", nargs="*", help="Properties as key=value")

    p_met_delete = sp_metrics.add_parser("delete", help="Delete metric value")
    p_met_delete.add_argument("id", help="Metric ID")

    p_met_update = sp_metrics.add_parser("update", help="Update metric value")
    p_met_update.add_argument("id", help="Metric ID")
    p_met_update.add_argument("props", nargs="*", help="Properties as key=value")

    # Metrics Global
    subparsers.add_parser("metrics-latest", help="Latest metrics")

    # Equipment
    p_equip = subparsers.add_parser("equipment", help="Equipment")
    sp_equip = p_equip.add_subparsers(dest="action", required=True)
    sp_equip.add_parser("list", help="List equipment")
    p_equip_get = sp_equip.add_parser("get", help="Get equipment")
    p_equip_get.add_argument("id", help="Equipment ID")
    
    sp_equip.add_parser("categories", help="List categories")
    p_equip_cat = sp_equip.add_parser("category", help="Get category")
    p_equip_cat.add_argument("id", help="Category ID")
    
    p_equip_cat_equip = sp_equip.add_parser("category-equipment", help="List equipment in category")
    p_equip_cat_equip.add_argument("id", help="Category ID")

    # Services
    subparsers.add_parser("services", help="Connected services")

    # Sync
    p_sync = subparsers.add_parser("sync", help="Sync")
    sp_sync = p_sync.add_subparsers(dest="action", required=True)
    p_sync_changes = sp_sync.add_parser("changes", help="Changed entities")
    p_sync_changes.add_argument("props", nargs="*", help="Properties as key=value")

    # Race Result
    p_race = subparsers.add_parser("raceresult", help="Race results")
    sp_race = p_race.add_subparsers(dest="action", required=True)
    sp_race.add_parser("list", help="List race results")
    p_race_get = sp_race.add_parser("get", help="Get race result")
    p_race_get.add_argument("id", help="Activity ID")
    
    p_race_delete = sp_race.add_parser("delete", help="Delete race result")
    p_race_delete.add_argument("id", help="Activity ID")

    p_race_update = sp_race.add_parser("update", help="Update race result")
    p_race_update.add_argument("id", help="Activity ID")
    p_race_update.add_argument("props", nargs="*", help="Properties as key=value")

    # Settings
    p_settings = subparsers.add_parser("settings", help="Settings")
    sp_settings = p_settings.add_subparsers(dest="action", required=True)
    sp_settings.add_parser("date-range", help="List date ranges")
    p_set_dr = sp_settings.add_parser("date-range-get", help="Get date range")
    p_set_dr.add_argument("id", help="ID")

    # Tag
    p_tag = subparsers.add_parser("tag", help="Tags")
    sp_tag = p_tag.add_subparsers(dest="action", required=True)
    sp_tag.add_parser("list", help="List tags")
    p_tag_get = sp_tag.add_parser("get", help="Get tag")
    p_tag_get.add_argument("id", help="Tag ID")

    # Statistics
    p_stats = subparsers.add_parser("statistics", help="Statistics")
    sp_stats = p_stats.add_subparsers(dest="action", required=True)
    sp_stats.add_parser("current", help="Current statistics summary")

    args = parser.parse_args()

    # Handle commands
    res = None
    if args.resource == "activity":
        if args.action == "list":
            res = make_request("/api/v1/activity")
        elif args.action == "get":
            res = make_request(f"/api/v1/activity/{args.id}")
        elif args.action == "export":
            res = make_request(f"/api/v1/activity/{args.id}/{args.format}")
        elif args.action == "upload":
            with open(args.file, "rb") as f:
                file_content = f.read()
            res = make_request("/api/v1/activities/uploads", method="POST", data=file_content, headers={"Content-Type": "application/octet-stream"})
        elif args.action == "upload-status":
            res = make_request(f"/api/v1/activities/uploads/{args.id}")
        
    elif args.resource == "metrics":
        path = f"/api/v1/metrics/{args.metric}"
        if args.action == "list":
            res = make_request(path)
        elif args.action == "get":
            res = make_request(f"{path}/{args.id}")
        elif args.action == "create":
            res = make_request(path, method="POST", data=parse_props(args.props))
        elif args.action == "delete":
            res = make_request(f"{path}/{args.id}", method="DELETE")
        elif args.action == "update":
            res = make_request(f"{path}/{args.id}", method="PATCH", data=parse_props(args.props))

    elif args.resource == "metrics-latest":
        res = make_request("/api/v1/metrics/latest")

    elif args.resource == "equipment":
        if args.action == "list":
            res = make_request("/api/v1/equipment")
        elif args.action == "get":
            res = make_request(f"/api/v1/equipment/{args.id}")
        elif args.action == "categories":
            res = make_request("/api/v1/equipment/category")
        elif args.action == "category":
            res = make_request(f"/api/v1/equipment/category/{args.id}")
        elif args.action == "category-equipment":
            res = make_request(f"/api/v1/equipment/category/{args.id}/equipment")

    elif args.resource == "services":
        res = make_request("/api/v1/my/services")

    elif args.resource == "sync":
        if args.action == "changes":
            res = make_request("/api/v1/sync/changes", method="POST", data=parse_props(args.props))

    elif args.resource == "raceresult":
        if args.action == "list":
            res = make_request("/api/v1/raceresult")
        elif args.action == "get":
            res = make_request(f"/api/v1/raceresult/{args.id}")
        elif args.action == "delete":
            res = make_request(f"/api/v1/raceresult/{args.id}", method="DELETE")
        elif args.action == "update":
            res = make_request(f"/api/v1/raceresult/{args.id}", method="PATCH", data=parse_props(args.props))

    elif args.resource == "settings":
        if args.action == "date-range":
            res = make_request("/api/v1/settings/date-range")
        elif args.action == "date-range-get":
            res = make_request(f"/api/v1/settings/date-range/{args.id}")

    elif args.resource == "tag":
        if args.action == "list":
            res = make_request("/api/v1/tag")
        elif args.action == "get":
            res = make_request(f"/api/v1/tag/{args.id}")

    elif args.resource == "statistics":
        if args.action == "current":
            res = make_request("/api/v1/statistics/current")

    if res is not None:
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
