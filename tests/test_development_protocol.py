import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.development import DevelopmentInterface  # noqa: E402
from capabilities.development_protocol import DevelopmentProtocol  # noqa: E402
from capabilities.runtime import CapabilityRuntime  # noqa: E402


class DevelopmentProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        (self.root / "hello.txt").write_text(
            "Hello from ZebraBravo.",
            encoding="utf-8",
        )

        self.runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={
                "filesystem.read",
                "git.read",
            },
        )

        interface = DevelopmentInterface(self.runtime)
        self.protocol = DevelopmentProtocol(interface)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_protocol_requires_mapping_request(self):
        result = self.protocol.handle("invalid")

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["code"],
            "invalid_request",
        )

    def test_protocol_generates_request_id(self):
        result = self.protocol.handle(
            {
                "operation": "project_info",
            }
        )

        self.assertTrue(result["ok"])
        self.assertIsInstance(
            result["request_id"],
            str,
        )
        self.assertTrue(result["request_id"])

    def test_protocol_preserves_request_id(self):
        result = self.protocol.handle(
            {
                "request_id": "test-123",
                "operation": "project_info",
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["request_id"],
            "test-123",
        )

    def test_protocol_reports_version(self):
        result = self.protocol.handle(
            {
                "operation": "project_info",
            }
        )

        self.assertEqual(
            result["version"],
            "1",
        )

    def test_protocol_rejects_unsupported_version(self):
        result = self.protocol.handle(
            {
                "version": "999",
                "operation": "project_info",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["code"],
            "unsupported_version",
        )

    def test_protocol_requires_operation(self):
        result = self.protocol.handle({})

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["code"],
            "invalid_request",
        )

    def test_protocol_rejects_unknown_operation(self):
        result = self.protocol.handle(
            {
                "operation": "delete",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["code"],
            "unsupported_operation",
        )

    def test_protocol_requires_mapping_payload(self):
        result = self.protocol.handle(
            {
                "operation": "read",
                "payload": "hello.txt",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["code"],
            "invalid_request",
        )

    def test_protocol_routes_project_info(self):
        result = self.protocol.handle(
            {
                "request_id": "project-info-test",
                "operation": "project_info",
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["operation"],
            "project_info",
        )
        self.assertEqual(
            result["data"]["workspace_root"],
            self.root.resolve().as_posix(),
        )

    def test_protocol_routes_read(self):
        result = self.protocol.handle(
            {
                "request_id": "read-test",
                "operation": "read",
                "payload": {
                    "path": "hello.txt",
                },
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["operation"],
            "read",
        )
        self.assertEqual(
            result["data"]["path"],
            "hello.txt",
        )
        self.assertEqual(
            result["data"]["content"],
            "Hello from ZebraBravo.",
        )
        self.assertEqual(
            result["data"]["provenance"]["workspace_root"],
            self.root.as_posix(),
        )
        self.assertEqual(
            result["data"]["provenance"]["path"],
            "hello.txt",
        )
        self.assertIsNone(
            result["data"]["provenance"]["git_log"],
        )
        self.assertEqual(
            result["data"]["provenance"]["git_error"]["code"],
            "git_failed",
        )

    def test_protocol_preserves_capability_failure(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
        )

        interface = DevelopmentInterface(runtime)
        protocol = DevelopmentProtocol(interface)

        result = protocol.handle(
            {
                "request_id": "permission-test",
                "operation": "read",
                "payload": {
                    "path": "hello.txt",
                },
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["request_id"],
            "permission-test",
        )
        self.assertEqual(
            result["operation"],
            "read",
        )
        self.assertEqual(
            result["code"],
            "permission_denied",
        )

    def test_protocol_has_no_write_operation(self):
        self.assertNotIn(
            "write",
            DevelopmentProtocol._OPERATIONS,
        )

    def test_protocol_has_no_delete_operation(self):
        self.assertNotIn(
            "delete",
            DevelopmentProtocol._OPERATIONS,
        )

    def test_protocol_requires_development_interface(self):
        with self.assertRaises(TypeError):
            DevelopmentProtocol(None)


if __name__ == "__main__":
    unittest.main()