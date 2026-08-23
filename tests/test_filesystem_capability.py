import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.plugins.filesystem import FileSystemCapability  # noqa: E402
from capabilities.context import CapabilityContext  # noqa: E402


class FileSystemCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        self.capability = FileSystemCapability()

        self.context = CapabilityContext(
            workspace_root=self.root,
            permissions=frozenset({"filesystem.read"}),
        )

        (self.root / "hello.txt").write_text(
            "Hello from ZebraBravo.",
            encoding="utf-8",
        )

        nested = self.root / "nested"
        nested.mkdir()

        (nested / "notes.txt").write_text(
            "ZebraBravo search test.\n"
            "The quick brown fox.\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_permission_and_context_are_required(self):
        context_without_permission = CapabilityContext(
            workspace_root=self.root,
        )

        result = self.capability.execute(
            {
                "operation": "read",
                "path": "hello.txt",
            },
            context_without_permission,
        )

        self.assertTrue(result.ok)

        result = self.capability.execute(
            {
                "operation": "read",
                "path": "hello.txt",
            },
            CapabilityContext(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "context_required")

    def test_list_workspace_directory(self):
        result = self.capability.execute(
            {
                "operation": "list",
                "path": ".",
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data["path"], ".")
        self.assertEqual(
            result.data["entries"],
            [
                {
                    "name": "hello.txt",
                    "path": "hello.txt",
                    "kind": "file",
                },
                {
                    "name": "nested",
                    "path": "nested",
                    "kind": "directory",
                },
            ],
        )

    def test_read_nested_file(self):
        result = self.capability.execute(
            {
                "operation": "read",
                "path": "nested/notes.txt",
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data,
            {
                "path": "nested/notes.txt",
                "content": (
                    "ZebraBravo search test.\n"
                    "The quick brown fox.\n"
                ),
            },
        )

    def test_stat_file(self):
        result = self.capability.execute(
            {
                "operation": "stat",
                "path": "hello.txt",
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data["path"], "hello.txt")
        self.assertEqual(result.data["kind"], "file")
        self.assertTrue(result.data["is_file"])
        self.assertFalse(result.data["is_directory"])

    def test_absolute_path_is_rejected(self):
        result = self.capability.execute(
            {
                "operation": "read",
                "path": str(self.root / "hello.txt"),
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

    def test_traversal_is_rejected(self):
        result = self.capability.execute(
            {
                "operation": "read",
                "path": "../outside.txt",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

    def test_missing_path_is_reported(self):
        result = self.capability.execute(
            {
                "operation": "read",
                "path": "missing.txt",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "path_not_found")

    def test_missing_operation_or_path_is_invalid(self):
        result = self.capability.execute(
            {
                "operation": "read",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

        result = self.capability.execute(
            {
                "path": "hello.txt",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

    def test_unsupported_operation_is_rejected(self):
        result = self.capability.execute(
            {
                "operation": "delete",
                "path": "hello.txt",
            },
            self.context,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "unsupported_operation")

    def test_search_finds_matches_recursively(self):
        result = self.capability.execute(
            {
                "operation": "search",
                "path": ".",
                "query": "search test",
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data["query"], "search test")
        self.assertEqual(
            result.data["matches"],
            [
                {
                    "path": "nested/notes.txt",
                    "line": 1,
                    "text": "ZebraBravo search test.",
                }
            ],
        )
        self.assertFalse(result.data["truncated"])

    def test_search_is_case_insensitive(self):
        result = self.capability.execute(
            {
                "operation": "search",
                "path": ".",
                "query": "ZEBRABRAVO",
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["matches"],
            [
                {
                    "path": "hello.txt",
                    "line": 1,
                    "text": "Hello from ZebraBravo.",
                },
                {
                    "path": "nested/notes.txt",
                    "line": 1,
                    "text": "ZebraBravo search test.",
                },
            ],
        )

    def test_search_respects_result_limit(self):
        result = self.capability.execute(
            {
                "operation": "search",
                "path": ".",
                "query": "zebra",
                "limit": 1,
            },
            self.context,
        )

        self.assertTrue(result.ok)
        self.assertEqual(len(result.data["matches"]), 1)
        self.assertEqual(
            result.data["matches"][0]["path"],
            "hello.txt",
        )
        self.assertTrue(result.data["truncated"])


if __name__ == "__main__":
    unittest.main()