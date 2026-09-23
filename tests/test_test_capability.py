import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext  # noqa: E402
from capabilities.executor import CapabilityExecutor  # noqa: E402
from capabilities.plugins.test import TestCapability  # noqa: E402
from capabilities.registry import CapabilityRegistry  # noqa: E402


class TestCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        registry = CapabilityRegistry()
        registry.register(TestCapability())

        self.executor = CapabilityExecutor(registry)

        self.context = CapabilityContext(
            workspace_root=PROJECT_ROOT,
            permissions={"test.run"},
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def execute(self, operation, **request):
        return self.executor.execute(
            "test",
            {
                "operation": operation,
                **request,
            },
            self.context,
        )

    def test_metadata_declares_test_side_effect(self):
        metadata = TestCapability.metadata

        self.assertEqual(metadata.name, "test")
        self.assertEqual(metadata.side_effect, "test")
        self.assertIn("test.run", metadata.required_permissions)

    def test_unsupported_operation_is_rejected(self):
        result = self.execute("coverage")

        self.assertEqual(result.code, "unsupported_operation")

    def test_permission_is_required(self):
        denied_context = CapabilityContext(
            workspace_root=PROJECT_ROOT,
        )

        result = self.executor.execute(
            "test",
            {"operation": "pytest"},
            denied_context,
        )

        self.assertEqual(result.code, "permission_denied")

    def test_workspace_context_is_required(self):
        context = CapabilityContext(
            permissions={"test.run"},
        )

        result = self.executor.execute(
            "test",
            {"operation": "pytest"},
            context,
        )

        self.assertEqual(result.code, "context_required")

    def test_invalid_request_type_is_rejected(self):
        result = self.executor.execute(
            "test",
            "pytest",
            self.context,
        )

        self.assertEqual(result.code, "invalid_request")


if __name__ == "__main__":
    unittest.main()
from unittest.mock import patch
from types import SimpleNamespace

from capabilities.plugins.test import TestCapability
from capabilities.context import CapabilityContext


def test_test_capability_returns_subprocess_result(tmp_path):
    capability = TestCapability()

    context = CapabilityContext(
        workspace_root=tmp_path,
        permissions=frozenset({"test.run"}),
    )

    completed = SimpleNamespace(
        returncode=0,
        stdout="3 passed in 0.05s",
        stderr="",
    )

    with patch(
        "capabilities.plugins.test.subprocess.run",
        return_value=completed,
    ) as run:
        result = capability.execute(
            {"operation": "pytest"},
            context,
        )

    assert result.ok is True
    assert result.code == "ok"
    assert result.data["operation"] == "pytest"
    assert result.data["returncode"] == 0
    assert result.data["stdout"] == "3 passed in 0.05s"
    assert result.data["stderr"] == ""
    run.assert_called_once()
