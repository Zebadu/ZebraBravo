import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext  # noqa: E402
from capabilities.executor import CapabilityExecutor  # noqa: E402
from capabilities.plugins.filesystem import FileSystemCapability  # noqa: E402
from capabilities.registry import CapabilityRegistry  # noqa: E402


class FileSystemCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()
        (self.root / "top.txt").write_text("top-level", encoding="utf-8")
        (self.root / "notes").mkdir()
        (self.root / "notes" / "nested.txt").write_text("nested content", encoding="utf-8")

        registry = CapabilityRegistry()
        registry.register(FileSystemCapability())
        self.executor = CapabilityExecutor(registry)
        self.context = CapabilityContext(
            workspace_root=self.root,
            permissions={"filesystem.read"},
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def execute(self, operation, path):
        return self.executor.execute(
            "filesystem",
            {"operation": operation, "path": path},
            self.context,
        )

    def test_list_workspace_directory(self):
        result = self.execute("list", ".")

        self.assertTrue(result.ok)
        self.assertEqual(result.data["path"], ".")
        self.assertEqual(
            result.data["entries"],
            [
                {"name": "notes", "path": "notes", "kind": "directory"},
                {"name": "top.txt", "path": "top.txt", "kind": "file"},
            ],
        )

    def test_read_nested_file(self):
        result = self.execute("read", "notes/nested.txt")

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data,
            {"path": "notes/nested.txt", "content": "nested content"},
        )

    def test_stat_file(self):
        result = self.execute("stat", "top.txt")

        self.assertTrue(result.ok)
        self.assertEqual(result.data["path"], "top.txt")
        self.assertEqual(result.data["kind"], "file")
        self.assertEqual(result.data["size"], len("top-level"))
        self.assertTrue(result.data["is_file"])
        self.assertFalse(result.data["is_directory"])

    def test_missing_path_is_reported(self):
        result = self.execute("read", "missing.txt")

        self.assertEqual(result.code, "path_not_found")

    def test_traversal_is_rejected(self):
        result = self.execute("read", "../outside.txt")

        self.assertEqual(result.code, "invalid_request")

    def test_absolute_path_is_rejected(self):
        result = self.execute("read", str(self.root / "top.txt"))

        self.assertEqual(result.code, "invalid_request")

    def test_unsupported_operation_is_rejected(self):
        result = self.execute("delete", "top.txt")

        self.assertEqual(result.code, "unsupported_operation")

    def test_permission_and_context_are_required(self):
        denied = CapabilityExecutor(self.executor.registry).execute(
            "filesystem",
            {"operation": "list", "path": "."},
            CapabilityContext(workspace_root=self.root),
        )
        self.assertEqual(denied.code, "permission_denied")

        missing_context = self.executor.execute(
            "filesystem",
            {"operation": "list", "path": "."},
            CapabilityContext(permissions={"filesystem.read"}),
        )
        self.assertEqual(missing_context.code, "context_required")

    def test_missing_operation_or_path_is_invalid(self):
        result = self.executor.execute("filesystem", {}, self.context)

        self.assertEqual(result.code, "invalid_request")
