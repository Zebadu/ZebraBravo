import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext  # noqa: E402
from capabilities.plugins.filesystem_write import FileWriteCapability  # noqa: E402


class FileWriteCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        self.capability = FileWriteCapability()

        self.context = CapabilityContext(
            workspace_root=self.root,
            permissions=frozenset({"filesystem.write"}),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_metadata_declares_write_side_effect_and_permission(self):
        self.assertEqual(
            self.capability.metadata.name,
            "filesystem_write",
        )
        self.assertEqual(
            self.capability.metadata.side_effect,
            "write",
        )
        self.assertEqual(
            self.capability.metadata.required_permissions,
            frozenset({"filesystem.write"}),
        )

    def test_write_creates_file(self):
        result = self.capability.execute(
            {
                "operation": "write",
                "path": "hello.txt",
                "content": "Hello from ZebraBravo.",
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["path"],
            "hello.txt",
        )
        self.assertEqual(
            result.data["bytes_written"],
            len("Hello from ZebraBravo.".encode("utf-8")),
        )
        self.assertEqual(
            (self.root / "hello.txt").read_text(
                encoding="utf-8",
            ),
            "Hello from ZebraBravo.",
        )

    def test_write_replaces_existing_file(self):
        target = self.root / "hello.txt"
        target.write_text(
            "Original content.",
            encoding="utf-8",
        )

        result = self.capability.execute(
            {
                "operation": "write",
                "path": "hello.txt",
                "content": "Replacement content.",
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            target.read_text(encoding="utf-8"),
            "Replacement content.",
        )

    def test_write_creates_nested_parent_directories(self):
        result = self.capability.execute(
            {
                "operation": "write",
                "path": "nested/notes/quest.txt",
                "content": "The Quest for Truth continues.",
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["path"],
            "nested/notes/quest.txt",
        )
        self.assertEqual(
            (self.root / "nested/notes/quest.txt").read_text(
                encoding="utf-8",
            ),
            "The Quest for Truth continues.",
        )

    def test_absolute_path_is_rejected(self):
        result = self.capability.execute(
            {
                "operation": "write",
                "path": str(self.root / "hello.txt"),
                "content": "Should not be written.",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

    def test_traversal_is_rejected(self):
        result = self.capability.execute(
            {
                "operation": "write",
                "path": "../outside.txt",
                "content": "Should not be written.",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

    def test_workspace_root_is_required(self):
        result = self.capability.execute(
            {
                "operation": "write",
                "path": "hello.txt",
                "content": "Should not be written.",
            },
            CapabilityContext(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "context_required")

    def test_operation_path_and_content_are_required(self):
        result = self.capability.execute(
            {
                "operation": "write",
                "path": "hello.txt",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

        result = self.capability.execute(
            {
                "operation": "write",
                "content": "Missing path.",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

        result = self.capability.execute(
            {
                "path": "hello.txt",
                "content": "Missing operation.",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

    def test_non_mapping_request_is_rejected(self):
        result = self.capability.execute(
            "write",
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

    def test_unsupported_operation_is_rejected(self):
        result = self.capability.execute(
            {
                "operation": "delete",
                "path": "hello.txt",
                "content": "Should not be written.",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "unsupported_operation")

    def test_directory_target_is_rejected(self):
        directory = self.root / "existing"
        directory.mkdir()

        result = self.capability.execute(
            {
                "operation": "write",
                "path": "existing",
                "content": "Should not replace a directory.",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")


if __name__ == "__main__":
    unittest.main()