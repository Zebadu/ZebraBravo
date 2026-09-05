import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from companion.client import CompanionClient, CompanionClientError, CompanionProtocolError


class CompanionClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "ok": True,
                                "service": "zebrabravo-development-bridge",
                                "version": "0.1",
                            }
                        ).encode("utf-8")
                    )
                    return

                self.send_response(404)
                self.end_headers()

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
                    "data": {"workspace_root": "C:/test"},
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
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def make_client(self, token=None):
        return CompanionClient(host="127.0.0.1", port=self.port, auth_token=token)

    def test_health(self):
        response = self.make_client().health()
        self.assertTrue(response["ok"])
        self.assertEqual(response["service"], "zebrabravo-development-bridge")
        self.assertEqual(response["version"], "0.1")

    def test_execute_sends_v1_authenticated_request(self):
        response = self.make_client("TEST-TOKEN").execute("project_info", {"example": True}, request_id="test-001")
        self.assertTrue(response["ok"])
        self.assertEqual(response["version"], "1")
        self.assertEqual(response["request_id"], "test-001")
        self.assertEqual(response["operation"], "project_info")
        self.assertEqual(response["code"], "ok")

    def test_execute_requires_authentication(self):
        with self.assertRaises(CompanionClientError):
            self.make_client().execute("project_info")

    def test_http_error_is_wrapped(self):
        client = self.make_client("TEST-TOKEN")
        client.port = self.port + 1
        with self.assertRaises(CompanionClientError):
            client.execute("project_info")

    def test_invalid_json_is_wrapped(self):
        class InvalidJsonHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"not-json")

            def log_message(self, format, *args):
                return

        server = HTTPServer(("127.0.0.1", 0), InvalidJsonHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            client = CompanionClient(host="127.0.0.1", port=server.server_address[1])
            with self.assertRaises(CompanionProtocolError):
                client.health()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
