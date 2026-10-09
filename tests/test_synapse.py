import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock, patch

from synapse.client import SynapseClient


class SynapseClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path != "/health":
                    self.send_response(404)
                    self.end_headers()
                    return

                response = {
                    "ok": True,
                    "service": "zebrabravo-development-bridge",
                    "version": "0.1",
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            def do_POST(self):
                if self.path != "/development":
                    self.send_response(404)
                    self.end_headers()
                    return

                authorization = self.headers.get("Authorization")
                content_length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(content_length).decode("utf-8"))

                if authorization != "Bearer TEST-TOKEN":
                    self.send_response(401)
                    self.end_headers()
                    return

                response = {
                    "version": body["version"],
                    "request_id": body["request_id"],
                    "operation": body["operation"],
                    "ok": True,
                    "data": {
                        "workspace_root": "C:/test/ZebraBravo",
                        "content": "Hello from Synapse.",
                        "provenance": {
                            "workspace_root": "C:/test/ZebraBravo",
                            "path": "hello.txt",
                        },
                    },
                    "message": "ok",
                    "code": "ok",
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            def log_message(self, format, *args):
                return

        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def make_client(self):
        return SynapseClient(
            f"http://127.0.0.1:{self.port}/development",
            "TEST-TOKEN",
        )

    def test_health_returns_expected_service_identity(self):
        response = self.make_client().health()

        self.assertTrue(response["ok"])
        self.assertEqual(
            response["service"],
            "zebrabravo-development-bridge",
        )
        self.assertEqual(response["version"], "0.1")

    def test_health_reports_unavailable_bridge(self):
        client = SynapseClient(
            "http://127.0.0.1:1/development",
            "TEST-TOKEN",
            timeout=0.5,
        )

        response = client.health()

        self.assertFalse(response["ok"])
        self.assertEqual(response["code"], "bridge_unavailable")

    def test_project_info_request(self):
        response = self.make_client().request(
            "project_info",
            request_id="test-project-info",
        )

        self.assertTrue(response["ok"])
        self.assertEqual(response["version"], "1")
        self.assertEqual(response["request_id"], "test-project-info")
        self.assertEqual(response["operation"], "project_info")
        self.assertEqual(
            response["data"]["workspace_root"],
            "C:/test/ZebraBravo",
        )

    def test_read_request_returns_content_and_provenance(self):
        response = self.make_client().request(
            "read",
            {"path": "hello.txt"},
            request_id="test-read",
        )

        self.assertTrue(response["ok"])
        self.assertEqual(response["operation"], "read")
        self.assertEqual(
            response["data"]["content"],
            "Hello from Synapse.",
        )
        self.assertEqual(
            response["data"]["provenance"]["workspace_root"],
            "C:/test/ZebraBravo",
        )
        self.assertEqual(
            response["data"]["provenance"]["path"],
            "hello.txt",
        )



    def test_request_reports_bridge_unavailable(self):
        with patch(
            "synapse.client.urlopen",
            side_effect=URLError("bridge offline"),
        ):
            response = self.make_client().request(
                "project_info",
                request_id="test-offline",
            )

        self.assertFalse(response["ok"])
        self.assertEqual(response["code"], "bridge_unavailable")
        self.assertEqual(response["request_id"], "test-offline")
        self.assertEqual(response["operation"], "project_info")

    def test_request_reports_http_error(self):
        error = HTTPError(
            "http://127.0.0.1/development",
            401,
            "Unauthorized",
            hdrs=None,
            fp=None,
        )
        with patch("synapse.client.urlopen", side_effect=error):
            response = self.make_client().request(
                "project_info",
                request_id="test-http-error",
            )

        self.assertFalse(response["ok"])
        self.assertEqual(response["code"], "http_error")
        self.assertEqual(response["request_id"], "test-http-error")
        self.assertEqual(response["operation"], "project_info")

    def test_request_reports_invalid_json_response(self):
        mocked_response = MagicMock()
        mocked_response.__enter__.return_value.read.return_value = b"not-json"

        with patch("synapse.client.urlopen", return_value=mocked_response):
            response = self.make_client().request(
                "project_info",
                request_id="test-invalid-json",
            )

        self.assertFalse(response["ok"])
        self.assertEqual(response["code"], "invalid_response")
        self.assertEqual(response["request_id"], "test-invalid-json")
        self.assertEqual(response["operation"], "project_info")

    def test_request_reports_non_object_json_response(self):
        mocked_response = MagicMock()
        mocked_response.__enter__.return_value.read.return_value = b"[]"

        with patch("synapse.client.urlopen", return_value=mocked_response):
            response = self.make_client().request(
                "project_info",
                request_id="test-wrong-response-type",
            )

        self.assertFalse(response["ok"])
        self.assertEqual(response["code"], "invalid_response")
        self.assertEqual(response["request_id"], "test-wrong-response-type")
        self.assertEqual(response["operation"], "project_info")

if __name__ == "__main__":
    unittest.main()