from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import secrets
import threading
from collections.abc import Mapping
from typing import Any, Optional


class DevelopmentBridge:
    def __init__(
        self,
        development_service,
        host: str = "127.0.0.1",
        port: int = 0,
        auth_token: Optional[str] = None,
    ) -> None:
        if development_service is None:
            raise TypeError("A development service is required.")

        if not hasattr(development_service, "handle"):
            raise TypeError(
                "Development service must provide a handle method."
            )

        if host not in {"127.0.0.1", "localhost"}:
            raise ValueError(
                "Development bridge must bind to the local machine only."
            )

        if not isinstance(port, int) or not 0 <= port <= 65535:
            raise ValueError("Bridge port must be between 0 and 65535.")

        if auth_token is not None and not isinstance(auth_token, str):
            raise TypeError("Authentication token must be a string or None.")

        self.development_service = development_service
        self.host = host
        self.port = port
        self.auth_token = auth_token or secrets.token_urlsafe(32)

        self._server: Optional[ThreadingHTTPServer] = None
        self._serving = False
        self._serve_thread: Optional[threading.Thread] = None

    @property
    def address(self) -> Optional[tuple[str, int]]:
        if self._server is None:
            return None

        host, port = self._server.server_address
        return host, port

    @property
    def is_running(self) -> bool:
        return self._serving

    def start(self) -> tuple[str, int]:
        if self._server is not None:
            raise RuntimeError("Development bridge is already running.")

        bridge = self

        class RequestHandler(BaseHTTPRequestHandler):
            server_version = "ZebraBravoDevelopmentBridge/0.1"

            def do_POST(self) -> None:
                if self.path != "/development":
                    self._send_json(
                        HTTPStatus.NOT_FOUND,
                        {
                            "ok": False,
                            "code": "not_found",
                            "message": "Unknown bridge endpoint.",
                        },
                    )
                    return

                if not self._authorized():
                    self._send_json(
                        HTTPStatus.UNAUTHORIZED,
                        {
                            "ok": False,
                            "code": "unauthorized",
                            "message": (
                                "Development bridge authentication failed."
                            ),
                        },
                    )
                    return

                try:
                    content_length = int(
                        self.headers.get("Content-Length", "0")
                    )
                except ValueError:
                    self._send_json(
                        HTTPStatus.BAD_REQUEST,
                        {
                            "ok": False,
                            "code": "invalid_content_length",
                            "message": "Content-Length must be an integer.",
                        },
                    )
                    return

                if content_length <= 0:
                    self._send_json(
                        HTTPStatus.BAD_REQUEST,
                        {
                            "ok": False,
                            "code": "invalid_request",
                            "message": "Request body is required.",
                        },
                    )
                    return

                try:
                    body = self.rfile.read(content_length)
                    request = json.loads(body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    self._send_json(
                        HTTPStatus.BAD_REQUEST,
                        {
                            "ok": False,
                            "code": "invalid_json",
                            "message": (
                                "Request body must contain valid UTF-8 JSON."
                            ),
                        },
                    )
                    return

                if not isinstance(request, Mapping):
                    self._send_json(
                        HTTPStatus.BAD_REQUEST,
                        {
                            "ok": False,
                            "code": "invalid_request",
                            "message": (
                                "Request body must be a JSON object."
                            ),
                        },
                    )
                    return

                try:
                    response = bridge.development_service.handle(request)
                except Exception as exc:
                    response = {
                        "ok": False,
                        "code": "bridge_error",
                        "message": str(exc),
                    }

                self._send_json(HTTPStatus.OK, response)

            def do_GET(self) -> None:
                if self.path != "/health":
                    self._send_json(
                        HTTPStatus.NOT_FOUND,
                        {
                            "ok": False,
                            "code": "not_found",
                            "message": "Unknown bridge endpoint.",
                        },
                    )
                    return

                self._send_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "service": "zebrabravo-development-bridge",
                        "version": "0.1",
                    },
                )

            def log_message(self, format: str, *args: Any) -> None:
                """Suppress default HTTP console logging."""

            def _authorized(self) -> bool:
                supplied = self.headers.get("Authorization", "")
                expected = f"Bearer {bridge.auth_token}"
                return secrets.compare_digest(supplied, expected)

            def _send_json(
                self,
                status: HTTPStatus,
                payload: Mapping[str, Any],
            ) -> None:
                encoded = json.dumps(payload).encode("utf-8")

                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        self._server = ThreadingHTTPServer(
            (self.host, self.port),
            RequestHandler,
        )

        return self.address

    def serve_forever(self) -> None:
        if self._server is None:
            raise RuntimeError("Development bridge has not been started.")

        self._serving = True
        try:
            self._server.serve_forever()
        finally:
            self._serving = False

    def start_background(self) -> tuple[str, int]:
        address = self.start()

        self._serve_thread = threading.Thread(
            target=self.serve_forever,
            name="zebrabravo-development-bridge",
            daemon=True,
        )
        self._serve_thread.start()

        return address

    def stop(self) -> None:
        if self._server is None:
            return

        if self._serving:
            self._server.shutdown()

        self._server.server_close()
        self._server = None
        self._serving = False
        self._serve_thread = None