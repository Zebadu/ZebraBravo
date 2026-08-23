import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.development import DevelopmentInterface  # noqa: E402
from capabilities.development_protocol import DevelopmentProtocol  # noqa: E402
from capabilities.development_transport import DevelopmentTransport  # noqa: E402
from capabilities.runtime import CapabilityRuntime  # noqa: E402


class DevelopmentTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        (self.root / "hello.txt").write_text(
            "Hello from ZebraBravo.",
            encoding="utf-8",
        )

        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={
                "filesystem.read",
                "git.read",
            },
        )

        interface = DevelopmentInterface(runtime)
        protocol = DevelopmentProtocol(interface)
        self.transport = DevelopmentTransport(protocol)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_transport_requires_protocol(self):
        with self.assertRaises(TypeError):
            DevelopmentTransport(None)

    def test_transport_requires_handle_method(self):
        with self.assertRaises(TypeError):
            DevelopmentTransport(object())

    def test_transport_rejects_non_mapping_request(self):
        result = self.transport.handle("read")

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["version"],
            "1",
        )
        self.assertIsNone(result["request_id"])
        self.assertIsNone(result["operation"])
        self.assertEqual(
            result["code"],
            "invalid_request",
        )

    def test_transport_routes_project_info(self):
        result = self.transport.handle(
            {
                "request_id": "transport-project-info",
                "operation": "project_info",
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["request_id"],
            "transport-project-info",
        )
        self.assertEqual(
            result["operation"],
            "project_info",
        )

    def test_transport_routes_read(self):
        result = self.transport.handle(
            {
                "request_id": "transport-read",
                "operation": "read",
                "request": {
                    "path": "hello.txt",
                },
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["request_id"],
            "transport-read",
        )
        self.assertEqual(
            result["operation"],
            "read",
        )
        self.assertEqual(
            result["data"],
            {
                "path": "hello.txt",
                "content": "Hello from ZebraBravo.",
            },
        )

    def test_transport_preserves_protocol_failure(self):
        result = self.transport.handle(
            {
                "request_id": "transport-failure",
                "operation": "delete",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["request_id"],
            "transport-failure",
        )
        self.assertEqual(
            result["code"],
            "unsupported_operation",
        )

    def test_transport_preserves_protocol_version_failure(self):
        result = self.transport.handle(
            {
                "request_id": "transport-version",
                "version": "999",
                "operation": "project_info",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["request_id"],
            "transport-version",
        )
        self.assertEqual(
            result["code"],
            "unsupported_version",
        )


if __name__ == "__main__":
    unittest.main()