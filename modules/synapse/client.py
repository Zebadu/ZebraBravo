import json
from urllib.request import Request, urlopen


class SynapseClient:
    """Thin client for the existing ZebraBravo DevelopmentBridge."""

    def __init__(self, url, auth_token, timeout=10):
        self.url = url
        self.auth_token = auth_token
        self.timeout = timeout

    def request(self, operation, payload=None, request_id=None):
        body = {
            "request_id": request_id,
            "version": "1",
            "operation": operation,
            "payload": payload or {},
        }

        request = Request(
            self.url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))
