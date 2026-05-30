#!/usr/bin/env python3
"""Mock Runalyze API server for integration testing.

Stubs all endpoints used by the CLI so we can test the full agent→CLI→API
round-trip without a real Runalyze account.
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler


class ReuseAddrHTTPServer(HTTPServer):
    allow_reuse_address = True
    allow_reuse_port = True


class MockRunalyzeHandler(BaseHTTPRequestHandler):
    ROUTES = {
        # Activities
        ("GET", "/api/v1/activity"): (200, {"hydra:member": [{"id": 1, "title": "Morning Run", "sport": "running"}]}),
        ("GET", "/api/v1/activity/1"): (200, {"id": 1, "title": "Morning Run", "sport": "running"}),
        # Export (returns text)
        ("GET", "/api/v1/activity/1/gpx"): (200, "<gpx><trk><name>Morning Run</name></trk></gpx>", "text/xml"),
        # Upload
        ("POST", "/api/v1/activities/uploads"): (201, {"id": "upload-123", "status": "pending"}),
        ("GET", "/api/v1/activities/uploads/upload-123"): (200, {"id": "upload-123", "status": "processed"}),
        # Metrics
        ("GET", "/api/v1/metrics/heartRateRest"): (200, {"hydra:member": [{"id": 1, "value": 60}]}),
        ("GET", "/api/v1/metrics/heartRateRest/1"): (200, {"id": 1, "value": 60}),
        ("POST", "/api/v1/metrics/heartRateRest"): (201, {"id": 2, "value": 55}),
        ("GET", "/api/v1/metrics/latest"): (200, {"heartRateRest": {"value": 58}}),
        # Equipment
        ("GET", "/api/v1/equipment"): (200, {"hydra:member": [{"id": 1, "name": "Nike Pegasus"}]}),
        ("GET", "/api/v1/equipment/1"): (200, {"id": 1, "name": "Nike Pegasus"}),
        ("GET", "/api/v1/equipment/category"): (200, {"hydra:member": [{"id": 1, "name": "Shoes"}]}),
        ("GET", "/api/v1/equipment/category/1"): (200, {"id": 1, "name": "Shoes"}),
        ("GET", "/api/v1/equipment/category/1/equipment"): (200, {"hydra:member": [{"id": 1, "name": "Nike Pegasus"}]}),
        # Race results
        ("GET", "/api/v1/raceresult"): (200, {"hydra:member": []}),
        # Tags
        ("GET", "/api/v1/tag"): (200, {"hydra:member": []}),
        # Settings
        ("GET", "/api/v1/settings/date-range"): (200, {"hydra:member": []}),
        # Statistics
        ("GET", "/api/v1/statistics/current"): (200, {"weekDistance": 42.5}),
        # Services (used for the install verification)
        ("GET", "/api/v1/my/services"): (200, ["activity", "metrics", "equipment"]),
        # Sync
        ("POST", "/api/v1/sync/changes"): (200, {"status": "synced"}),
    }

    def _handle(self, method):
        path = self.path.split("?")[0]  # strip query params

        key = (method, path)
        if key in self.ROUTES:
            status, *rest = self.ROUTES[key]
            content_type = "application/json"
            body = rest[0]
            if len(rest) > 1:
                content_type = rest[1]

            self.send_response(status)
            self.send_header("Content-Type", content_type)

            if isinstance(body, str) and not body.startswith("{"):
                # Plain text / XML response
                encoded = body.encode("utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
            else:
                encoded = json.dumps(body).encode("utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            body = json.dumps({"error": "not found", "path": path}).encode("utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PATCH(self):
        self._handle("PATCH")

    def do_DELETE(self):
        self._handle("DELETE")

    def log_message(self, format, *args):
        # Quiet logging — only print to stderr
        print(f"[mock-api] {args[0]}", file=sys.stderr)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18080
    server = ReuseAddrHTTPServer(("127.0.0.1", port), MockRunalyzeHandler)
    print(json.dumps({"mock_api": "running", "port": port}))
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
