import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.development_service import DevelopmentService  # noqa: E402
from capabilities.runtime import CapabilityRuntime  # noqa: E402


class DevelopmentServiceTests(unittest.TestCase):
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
            permissions={"filesystem.read"},
        )

        self.service = DevelopmentService(runtime)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_service_requires_runtime(self):
        with self.assertRaises(TypeError):
            DevelopmentService(None)

    def test_service_assembles_protocol(self):
        self.assertIsNotNone(self.service.protocol)

    def test_service_assembles_transport(self):
        self.assertIsNotNone(self.service.transport)

    def test_service_routes_project_info(self):
        result = self.service.handle(
            {
                "request_id": "service-project-info",
                "operation": "project_info",
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["request_id"],
            "service-project-info",
        )
        self.assertEqual(
            result["operation"],
            "project_info",
        )

    def test_service_routes_read(self):
        result = self.service.handle(
            {
                "request_id": "service-read",
                "operation": "read",
                "request": {
                    "path": "hello.txt",
                },
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["request_id"],
            "service-read",
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

    def test_service_preserves_permission_boundary(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions=set(),
        )

        service = DevelopmentService(runtime)

        result = service.handle(
            {
                "request_id": "service-denied",
                "operation": "read",
                "request": {
                    "path": "hello.txt",
                },
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["request_id"],
            "service-denied",
        )
        self.assertEqual(
            result["code"],
            "permission_denied",
        )

    def test_service_preserves_protocol_boundary(self):
        result = self.service.handle(
            {
                "request_id": "service-delete",
                "operation": "delete",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["request_id"],
            "service-delete",
        )
        self.assertEqual(
            result["operation"],
            None,
        )
        self.assertEqual(
            result["code"],
            "unsupported_operation",
        )


if __name__ == "__main__":
    unittest.main()