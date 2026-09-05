import json
import urllib.error
from urllib import request


class CompanionClientError(Exception):
    """Base exception for Companion client failures."""


class CompanionProtocolError(CompanionClientError):
    """Raised when ZebraBravo returns an invalid protocol response."""


class CompanionClient:
    """Small client for the local ZebraBravo Development Bridge."""

    def __init__(
        self,
        host="127.0.0.1",
        port=52336,
        auth_token=None,
        timeout=5.0,
    ):
        self.host = host
        self.port = port
        self.auth_token = auth_token
        self.timeout = timeout

    @property
    def base_url(self):
        return f"http://{self.host}:{self.port}"

    def health(self):
        """Return the Development Bridge health response."""
        return self._get("/health")

    def execute(self, operation, payload=None, request_id="companion-1"):
        """Execute one permitted Development Protocol operation."""
        if payload is None:
            payload = {}

        body = {
            "version": "1",
            "request_id": request_id,
            "operation": operation,
            "payload": payload,
        }

        return self._post("/development", body)

    def _get(self, path):
        url = f"{self.base_url}{path}"
        req = request.Request(url, method="GET")

        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                return self._decode_response(response)
        except urllib.error.HTTPError as exc:
            raise CompanionClientError(
                f"Development Bridge returned HTTP {exc.code}."
            ) from exc
        except urllib.error.URLError as exc:
            raise CompanionClientError(
                "Unable to connect to the Development Bridge."
            ) from exc

    def _post(self, path, body):
        if not self.auth_token:
            raise CompanionClientError(
                "Development Bridge authentication token is required."
            )

        data = json.dumps(body).encode("utf-8")
        url = f"{self.base_url}{path}"
        req = request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth_token}",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                return self._decode_response(response)
        except urllib.error.HTTPError as exc:
            raise CompanionClientError(
                f"Development Bridge returned HTTP {exc.code}."
            ) from exc
        except urllib.error.URLError as exc:
            raise CompanionClientError(
                "Unable to connect to the Development Bridge."
            ) from exc

    @staticmethod
    def _decode_response(response):
        try:
            body = response.read().decode("utf-8")
            return json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CompanionProtocolError(
                "Development Bridge returned an invalid JSON response."
            ) from exc