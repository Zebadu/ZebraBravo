import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class SynapseClient:
    """Thin client for the existing ZebraBravo DevelopmentBridge."""

    def __init__(self, url, auth_token, timeout=10):
        self.url = url
        self.auth_token = auth_token
        self.timeout = timeout

    def health(self):
        url = self.url.rsplit("/", 1)[0] + "/health"
        try:
            request = Request(url, method="GET")
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, UnicodeDecodeError) as exc:
            if isinstance(exc, HTTPError):
                return {"ok": False, "code": "health_http_error",
                        "message": f"HTTP {exc.code}"}
            if isinstance(exc, (URLError, TimeoutError, OSError)):
                return {"ok": False, "code": "bridge_unavailable",
                        "message": str(exc)}
            if isinstance(exc, (ValueError, UnicodeDecodeError)):
                return {"ok": False, "code": "invalid_health_response",
                        "message": str(exc)}
            raise

        if not isinstance(result, dict):
            return {"ok": False, "code": "invalid_health_response",
                    "message": "Health response must be a JSON object."}

        if (result.get("ok") is not True
                or result.get("service") != "zebrabravo-development-bridge"
                or result.get("version") != "0.1"):
            return {"ok": False, "code": "unexpected_health_response",
                    "data": result}

        return {"ok": True, "service": result["service"],
                "version": result["version"]}

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

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return {
                "ok": False,
                "code": "http_error",
                "message": f"HTTP {exc.code}",
                "request_id": request_id,
                "operation": operation,
            }
        except (URLError, TimeoutError, OSError) as exc:
            return {
                "ok": False,
                "code": "bridge_unavailable",
                "message": str(exc),
                "request_id": request_id,
                "operation": operation,
            }
        except (ValueError, UnicodeDecodeError) as exc:
            return {
                "ok": False,
                "code": "invalid_response",
                "message": str(exc),
                "request_id": request_id,
                "operation": operation,
            }
