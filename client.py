import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class RunalyzeAPIError(Exception):
    """Custom exception for Runalyze API errors."""

    pass


class RunalyzeClient:
    def __init__(self, token, base_url=None):
        self.token = token
        self.base_url = base_url or os.getenv(
            "RUNALYZE_BASE_URL", "https://runalyze.com"
        )
        if not self.token:
            raise RunalyzeAPIError("RUNALYZE_AUTH_TOKEN not found.")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "token": self.token,
                "Accept": "application/json",
            }
        )

        # Rate limiting / Retry support
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request(
        self,
        method,
        path,
        data=None,
        headers=None,
        is_binary=False,
        paginate=False,
        limit=None,
    ):
        url = self.base_url + path

        try:
            results = []

            while True:
                current_url = url

                if is_binary:
                    response = self.session.request(
                        method, current_url, data=data, headers=headers
                    )
                else:
                    response = self.session.request(
                        method, current_url, json=data, headers=headers
                    )

                response.raise_for_status()

                if response.status_code == 204:
                    return {"status": "success"}

                content_type = response.headers.get("Content-Type", "")
                if (
                    "application/json" not in content_type
                    and "application/ld+json" not in content_type
                ):
                    return response.content

                res_data = response.json()

                if not paginate:
                    return res_data

                # Handle Hydra pagination (JSON-LD)
                if isinstance(res_data, dict) and "hydra:member" in res_data:
                    member = res_data.get("hydra:member", [])
                    results.extend(member)

                    if limit is not None and len(results) >= limit:
                        return results[:limit]

                    next_page = res_data.get("hydra:view", {}).get("hydra:next")
                    if next_page:
                        if not next_page.startswith("http"):
                            url = self.base_url + next_page
                        else:
                            url = next_page
                    else:
                        break
                # Fallback for simple list pagination if it exists
                elif isinstance(res_data, list):
                    if not res_data:
                        break
                    results.extend(res_data)
                    if limit is not None and len(results) >= limit:
                        return results[:limit]
                    break
                else:
                    return res_data

            return results

        except requests.exceptions.RequestException as e:
            error_msg = f"{e}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_msg += f"\n{e.response.text}"
                except Exception:
                    pass
            raise RunalyzeAPIError(error_msg)

    # Activity Methods
    def get_activities(self, limit=None):
        return self.request("GET", "/api/v1/activity", paginate=True, limit=limit)

    def get_activity(self, activity_id):
        return self.request("GET", f"/api/v1/activity/{activity_id}")

    def export_activity(self, activity_id, format):
        return self.request("GET", f"/api/v1/activity/{activity_id}/{format}")

    def upload_activity(self, file_content):
        return self.request(
            "POST",
            "/api/v1/activities/uploads",
            data=file_content,
            headers={"Content-Type": "application/octet-stream"},
            is_binary=True,
        )

    def get_upload_status(self, upload_id):
        return self.request("GET", f"/api/v1/activities/uploads/{upload_id}")

    # Metrics Methods
    def get_metrics(self, metric_type, limit=None):
        return self.request(
            "GET", f"/api/v1/metrics/{metric_type}", paginate=True, limit=limit
        )

    def get_metric(self, metric_type, metric_id):
        return self.request("GET", f"/api/v1/metrics/{metric_type}/{metric_id}")

    def create_metric(self, metric_type, data):
        return self.request("POST", f"/api/v1/metrics/{metric_type}", data=data)

    def delete_metric(self, metric_type, metric_id):
        return self.request("DELETE", f"/api/v1/metrics/{metric_type}/{metric_id}")

    def update_metric(self, metric_type, metric_id, data):
        return self.request(
            "PATCH", f"/api/v1/metrics/{metric_type}/{metric_id}", data=data
        )

    def get_latest_metrics(self):
        return self.request("GET", "/api/v1/metrics/latest")

    # Equipment Methods
    def get_equipment(self, limit=None):
        return self.request("GET", "/api/v1/equipment", paginate=True, limit=limit)

    def get_equipment_item(self, equipment_id):
        return self.request("GET", f"/api/v1/equipment/{equipment_id}")

    def get_equipment_categories(self, limit=None):
        return self.request(
            "GET", "/api/v1/equipment/category", paginate=True, limit=limit
        )

    def get_equipment_category(self, category_id):
        return self.request("GET", f"/api/v1/equipment/category/{category_id}")

    def get_equipment_by_category(self, category_id, limit=None):
        return self.request(
            "GET",
            f"/api/v1/equipment/category/{category_id}/equipment",
            paginate=True,
            limit=limit,
        )

    # Service & Sync Methods
    def get_services(self):
        return self.request("GET", "/api/v1/my/services")

    def sync_changes(self, data):
        return self.request("POST", "/api/v1/sync/changes", data=data)

    # Race Result Methods
    def get_race_results(self, limit=None):
        return self.request("GET", "/api/v1/raceresult", paginate=True, limit=limit)

    def get_race_result(self, result_id):
        return self.request("GET", f"/api/v1/raceresult/{result_id}")

    def delete_race_result(self, result_id):
        return self.request("DELETE", f"/api/v1/raceresult/{result_id}")

    def update_race_result(self, result_id, data):
        return self.request("PATCH", f"/api/v1/raceresult/{result_id}", data=data)

    # Settings Methods
    def get_settings_date_ranges(self, limit=None):
        return self.request(
            "GET", "/api/v1/settings/date-range", paginate=True, limit=limit
        )

    def get_settings_date_range(self, range_id):
        return self.request("GET", f"/api/v1/settings/date-range/{range_id}")

    # Tag Methods
    def get_tags(self, limit=None):
        return self.request("GET", "/api/v1/tag", paginate=True, limit=limit)

    def get_tag(self, tag_id):
        return self.request("GET", f"/api/v1/tag/{tag_id}")

    # Statistics Methods
    def get_current_statistics(self):
        return self.request("GET", "/api/v1/statistics/current")
