import sys
import tempfile
import unittest
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

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_runtime_registers_capabilities(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
        )

        self.assertEqual(
            runtime.capability_names(),
            ("filesystem", "truth"),
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