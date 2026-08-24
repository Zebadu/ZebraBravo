import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.development_service import DevelopmentService  # noqa: E402
from capabilities.runtime import CapabilityRuntime  # noqa: E402


class DevelopmentRuntimeTests(unittest.TestCase):
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
            permissions={"filesystem.read"},
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_runtime_exposes_development_service(self):
        self.assertIsInstance(
            self.runtime.development_service,
            DevelopmentService,
        )

    def test_runtime_development_service_routes_read(self):
        result = self.runtime.execute_development(
            {
                "request_id": "runtime-read",
                "operation": "read",
                "request": {
                    "path": "hello.txt",
                },
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["request_id"],
            "runtime-read",
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

    def test_runtime_development_service_preserves_permission_boundary(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions=set(),
        )

        result = runtime.execute_development(
            {
                "request_id": "runtime-denied",
                "operation": "read",
                "request": {
                    "path": "hello.txt",
                },
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["request_id"],
            "runtime-denied",
        )
        self.assertEqual(
            result["code"],
            "permission_denied",
        )

    def test_runtime_development_service_preserves_protocol_boundary(self):
        result = self.runtime.execute_development(
            {
                "request_id": "runtime-delete",
                "operation": "delete",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["request_id"],
            "runtime-delete",
        )
        self.assertEqual(
            result["code"],
            "unsupported_operation",
        )


if __name__ == "__main__":
    unittest.main()