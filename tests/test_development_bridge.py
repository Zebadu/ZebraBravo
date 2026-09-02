import json
import urllib.error
import urllib.request

from modules.capabilities.development_bridge import DevelopmentBridge


class FakeDevelopmentService:
    def handle(self, request):
        return {
            "ok": True,
            "echo": request,
        }


def test_bridge_starts_and_stops():
    bridge = DevelopmentBridge(
        FakeDevelopmentService(),
        auth_token="TEST-TOKEN",
    )

    assert bridge.address is None
    assert bridge.is_running is False

    address = bridge.start_background()

    assert address[0] == "127.0.0.1"
    assert address[1] > 0
    assert bridge.address == address

    bridge.stop()

    assert bridge.address is None
    assert bridge.is_running is False


def test_bridge_health_endpoint():
    bridge = DevelopmentBridge(
        FakeDevelopmentService(),
        auth_token="TEST-TOKEN",
    )

    host, port = bridge.start_background()

    try:
        response = urllib.request.urlopen(
            f"http://{host}:{port}/health"
        )

        payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload["ok"] is True
        assert payload["service"] == "zebrabravo-development-bridge"
        assert payload["version"] == "0.1"
    finally:
        bridge.stop()


def test_bridge_rejects_missing_authentication():
    bridge = DevelopmentBridge(
        FakeDevelopmentService(),
        auth_token="TEST-TOKEN",
    )

    host, port = bridge.start_background()

    try:
        request = urllib.request.Request(
            f"http://{host}:{port}/development",
            data=json.dumps(
                {
                    "operation": "project_info",
                    "request": {},
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
        )

        try:
            urllib.request.urlopen(request)
            assert False, "Unauthenticated request should be rejected."
        except urllib.error.HTTPError as error:
            assert error.code == 401

            payload = json.loads(
                error.read().decode("utf-8")
            )

            assert payload["ok"] is False
            assert payload["code"] == "unauthorized"
    finally:
        bridge.stop()


def test_bridge_accepts_valid_authentication():
    bridge = DevelopmentBridge(
        FakeDevelopmentService(),
        auth_token="TEST-TOKEN",
    )

    host, port = bridge.start_background()

    try:
        request = urllib.request.Request(
            f"http://{host}:{port}/development",
            data=json.dumps(
                {
                    "operation": "project_info",
                    "request": {},
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer TEST-TOKEN",
            },
        )

        response = urllib.request.urlopen(request)

        payload = json.loads(
            response.read().decode("utf-8")
        )

        assert response.status == 200
        assert payload["ok"] is True
        assert payload["echo"]["operation"] == "project_info"
    finally:
        bridge.stop()