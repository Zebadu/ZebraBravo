import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.contracts import CapabilityResult
from capabilities.runtime import CapabilityRuntime


class FakeDesktopGateway:
    def __init__(self, result=None):
        self.result = result or CapabilityResult(
            ok=True,
            data={
                "windows": [
                    {
                        "title": "Test Window",
                        "control_type": "Window",
                        "visible": True,
                        "enabled": True,
                    }
                ]
            },
        )
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return self.result


class DesktopRuntimeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.desktop_gateway = FakeDesktopGateway()

        self.runtime = CapabilityRuntime(
            permissions={"desktop.read"},
            dependencies={
                "desktop_gateway": self.desktop_gateway,
            },
        )

    def test_desktop_capability_is_registered(self):
        self.assertIn(
            "desktop",
            self.runtime.capability_names(),
        )

    def test_desktop_request_travels_through_full_runtime_spine(self):
        request = {
            "operation": "inspect",
        }

        result = self.runtime.execute(
            "desktop",
            request,
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["windows"][0]["title"],
            "Test Window",
        )
        self.assertEqual(
            self.desktop_gateway.requests,
            [request],
        )

    def test_desktop_requires_explicit_permission(self):
        runtime = CapabilityRuntime(
            dependencies={
                "desktop_gateway": self.desktop_gateway,
            },
        )

        result = runtime.execute(
            "desktop",
            {
                "operation": "inspect",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(
            result.code,
            "permission_denied",
        )

    def test_desktop_dependency_is_passed_through_context(self):
        dependency = self.runtime.context.get_dependency(
            "desktop_gateway"
        )

        self.assertIs(
            dependency,
            self.desktop_gateway,
        )

    def test_desktop_gateway_failure_is_preserved(self):
        expected = CapabilityResult(
            ok=False,
            code="desktop_unavailable",
            message="Desktop Gateway unavailable.",
        )

        gateway = FakeDesktopGateway(expected)

        runtime = CapabilityRuntime(
            permissions={"desktop.read"},
            dependencies={
                "desktop_gateway": gateway,
            },
        )

        result = runtime.execute(
            "desktop",
            {
                "operation": "inspect",
            },
        )

        self.assertIs(
            result,
            expected,
        )


if __name__ == "__main__":
    unittest.main()
