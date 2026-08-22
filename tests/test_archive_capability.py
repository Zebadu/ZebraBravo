import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext  # noqa: E402
from capabilities.executor import CapabilityExecutor  # noqa: E402
from capabilities.plugins.archive import ArchiveCapability  # noqa: E402
from capabilities.registry import CapabilityRegistry  # noqa: E402


class ArchiveCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        self.archive_path = self.root / "sample.zip"

        with zipfile.ZipFile(self.archive_path, "w") as archive:
            archive.writestr("top.txt", "top-level")
            archive.writestr("notes/nested.txt", "nested content")

        registry = CapabilityRegistry()
        registry.register(ArchiveCapability())
        self.executor = CapabilityExecutor(registry)

        self.context = CapabilityContext(
            workspace_root=self.root,
            permissions={"archive.read"},
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def execute(self, operation, archive_path="sample.zip", member=None):
        request = {
            "operation": operation,
            "path": archive_path,
        }

        if member is not None:
            request["member"] = member

        return self.executor.execute(
            "archive",
            request,
            self.context,
        )

    def test_list_archive_members(self):
        result = self.execute("list")

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data,
            {
                "path": "sample.zip",
                "members": [
                    {
                        "name": "notes/nested.txt",
                        "kind": "file",
                        "size": len("nested content"),
                    },
                    {
                        "name": "top.txt",
                        "kind": "file",
                        "size": len("top-level"),
                    },
                ],
            },
        )

    def test_read_archive_member(self):
        result = self.execute(
            "read",
            member="notes/nested.txt",
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data,
            {
                "path": "sample.zip",
                "member": "notes/nested.txt",
                "content": "nested content",
            },
        )

    def test_missing_archive_is_reported(self):
        result = self.execute(
            "list",
            archive_path="missing.zip",
        )

        self.assertEqual(result.code, "path_not_found")

    def test_non_archive_file_is_rejected(self):
        text_path = self.root / "not_archive.txt"
        text_path.write_text("plain text", encoding="utf-8")

        result = self.execute(
            "list",
            archive_path="not_archive.txt",
        )

        self.assertEqual(result.code, "invalid_archive")

    def test_archive_path_traversal_is_rejected(self):
        result = self.execute(
            "list",
            archive_path="../outside.zip",
        )

        self.assertEqual(result.code, "invalid_request")

    def test_archive_absolute_path_is_rejected(self):
        result = self.execute(
            "list",
            archive_path=str(self.archive_path),
        )

        self.assertEqual(result.code, "invalid_request")

    def test_member_traversal_is_rejected(self):
        result = self.execute(
            "read",
            member="../outside.txt",
        )

        self.assertEqual(result.code, "invalid_request")

    def test_missing_member_is_reported(self):
        result = self.execute(
            "read",
            member="missing.txt",
        )

        self.assertEqual(result.code, "member_not_found")

    def test_unsupported_operation_is_rejected(self):
        result = self.execute("extract")

        self.assertEqual(result.code, "unsupported_operation")

    def test_permission_is_required(self):
        denied = self.executor.execute(
            "archive",
            {"operation": "list", "path": "sample.zip"},
            CapabilityContext(workspace_root=self.root),
        )

        self.assertEqual(denied.code, "permission_denied")

    def test_missing_operation_or_path_is_invalid(self):
        result = self.executor.execute(
            "archive",
            {},
            self.context,
        )

        self.assertEqual(result.code, "invalid_request")

    def test_archive_remains_unchanged_after_read(self):
        original_size = self.archive_path.stat().st_size

        result = self.execute(
            "read",
            member="top.txt",
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            self.archive_path.stat().st_size,
            original_size,
        )
        self.assertTrue(zipfile.is_zipfile(self.archive_path))


if __name__ == "__main__":
    unittest.main()