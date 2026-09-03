import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.development import DevelopmentInterface
from capabilities.runtime import CapabilityRuntime


class DevelopmentInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        (self.root / "hello.txt").write_text(
            "Hello from ZebraBravo.",
            encoding="utf-8",
        )

        notes_dir = self.root / "notes"
        notes_dir.mkdir()

        (notes_dir / "quest.txt").write_text(
            "The Quest for Truth continues.",
            encoding="utf-8",
        )

        self.runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={
                "filesystem.read",
                "git.read",
            },
        )

        self.interface = DevelopmentInterface(self.runtime)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_project_info_reports_workspace_and_capabilities(self):
        result = self.interface.execute("project_info")

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["workspace_root"],
            self.root.as_posix(),
        )
        self.assertEqual(
            result.data["capabilities"],
            (
                "archive",
                "filesystem",
                "filesystem_write",
                "git",
                "powershell_xray",
                "truth",
                "visual",
            ),
        )

    def test_read_travels_through_runtime(self):
        result = self.interface.execute(
            "read",
            {
                "path": "hello.txt",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["path"],
            "hello.txt",
        )
        self.assertEqual(
            result.data["content"],
            "Hello from ZebraBravo.",
        )
        self.assertEqual(
            result.data["provenance"]["workspace_root"],
            self.root.as_posix(),
        )
        self.assertEqual(
            result.data["provenance"]["path"],
            "hello.txt",
        )
        self.assertIsNone(
            result.data["provenance"]["git_log"],
        )
        self.assertEqual(
            result.data["provenance"]["git_error"]["code"],
            "git_failed",
        )

    def test_list_travels_through_runtime(self):
        result = self.interface.execute(
            "list",
            {
                "path": ".",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["path"],
            ".",
        )

    def test_search_travels_through_runtime(self):
        result = self.interface.execute(
            "search",
            {
                "query": "Quest",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["query"],
            "Quest",
        )
        self.assertEqual(
            result.data["matches"],
            [
                {
                    "path": "notes/quest.txt",
                    "line": 1,
                    "text": "The Quest for Truth continues.",
                },
            ],
        )

    def test_search_accepts_path(self):
        result = self.interface.execute(
            "search",
            {
                "query": "Hello",
                "path": ".",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["query"],
            "Hello",
        )
        self.assertEqual(
            result.data["matches"],
            [
                {
                    "path": "hello.txt",
                    "line": 1,
                    "text": "Hello from ZebraBravo.",
                },
            ],
        )

    def test_search_requires_filesystem_permission(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
        )
        interface = DevelopmentInterface(runtime)

        result = interface.execute(
            "search",
            {
                "query": "Quest",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "permission_denied")

    def test_search_requires_query(self):
        result = self.interface.execute(
            "search",
            {
                "path": ".",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")

    def test_write_requires_confirmation(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={
                "filesystem.read",
                "filesystem.write",
            },
        )
        interface = DevelopmentInterface(runtime)

        result = interface.execute(
            "write",
            {
                "path": "written.txt",
                "content": "Written through ZebraBravo.",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "confirmation_required")
        self.assertEqual(
            result.data,
            {
                "side_effect": "write",
            },
        )
        self.assertFalse(
            (self.root / "written.txt").exists(),
        )

    def test_git_status_requires_git_permission(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
        )
        interface = DevelopmentInterface(runtime)

        result = interface.execute("git_status")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "permission_denied")

    def test_git_log_requires_git_permission(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
        )
        interface = DevelopmentInterface(runtime)

        result = interface.execute("git_log")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "permission_denied")

    def test_git_log_travels_through_runtime(self):
        subprocess.run(
            ["git", "init"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            ["git", "config", "user.email", "zebrabravo@test.local"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            ["git", "config", "user.name", "ZebraBravo Test"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            ["git", "add", "."],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            ["git", "commit", "-m", "Initial test commit"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )

        result = self.interface.execute(
            "git_log",
            {
                "limit": 1,
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["operation"],
            "log",
        )
        self.assertEqual(
            result.data["limit"],
            1,
        )
        self.assertIn(
            "Initial test commit",
            result.data["output"],
        )

    def test_git_diff_travels_through_runtime(self):
        result = self.interface.execute(
            "git_diff",
            {
                "staged": False,
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "git_failed")

    def test_unknown_operation_is_rejected(self):
        result = self.interface.execute("delete")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "unsupported_operation")

    def test_non_mapping_request_is_rejected(self):
        result = self.interface.execute(
            "read",
            "hello.txt",
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "invalid_request")


if __name__ == "__main__":
    unittest.main()
