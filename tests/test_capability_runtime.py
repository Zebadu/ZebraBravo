import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime  # noqa: E402


class CapabilityRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        (self.root / "hello.txt").write_text(
            "Hello from ZebraBravo.",
            encoding="utf-8",
        )

        self.archive_path = self.root / "sample.zip"

        with zipfile.ZipFile(self.archive_path, "w") as archive:
            archive.writestr(
                "youtube/history.txt",
                "YouTube history test data.",
            )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_runtime_registers_capabilities(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
        )

        self.assertEqual(
            runtime.capability_names(),
            (
                "archive",
                "filesystem",
                "git",
                "powershell_xray",
                "truth",
                "visual",
            ),
        )

    def test_allowed_read_travels_through_full_action_spine(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
        )

        result = runtime.execute(
            "filesystem",
            {
                "operation": "read",
                "path": "hello.txt",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data,
            {
                "path": "hello.txt",
                "content": "Hello from ZebraBravo.",
            },
        )

    def test_archive_read_travels_through_full_action_spine(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"archive.read"},
        )

        result = runtime.execute(
            "archive",
            {
                "operation": "read",
                "path": "sample.zip",
                "member": "youtube/history.txt",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data,
            {
                "path": "sample.zip",
                "member": "youtube/history.txt",
                "content": "YouTube history test data.",
            },
        )

    def test_archive_requires_explicit_permission(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
        )

        result = runtime.execute(
            "archive",
            {
                "operation": "list",
                "path": "sample.zip",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "permission_denied")

    def test_policy_can_block_capability_before_execution(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
            denied_capabilities={"filesystem"},
        )

        result = runtime.execute(
            "filesystem",
            {
                "operation": "read",
                "path": "hello.txt",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "capability_denied")

    def test_runtime_passes_dependencies_into_capability_context(self):
        truth_service = object()

        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
            dependencies={
                "truth_gate": truth_service,
            },
        )

        self.assertIs(
            runtime.context.get_dependency("truth_gate"),
            truth_service,
        )


if __name__ == "__main__":
    unittest.main()