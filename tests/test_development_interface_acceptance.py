import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"

sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime
from assistant import Assistant


class DevelopmentInterfaceAcceptanceTests(unittest.TestCase):
    """Acceptance tests for ZebraBravo's controlled read-only development boundary."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        (self.root / "README.md").write_text(
            "# ZebraBravo\n\nControlled development interface.\n",
            encoding="utf-8",
        )

        modules_dir = self.root / "modules"
        modules_dir.mkdir()

        (modules_dir / "example.py").write_text(
            "def zebra_bravo():\n"
            "    return 'controlled'\n",
            encoding="utf-8",
        )

        tests_dir = self.root / "tests"
        tests_dir.mkdir()

        (tests_dir / "example_test.py").write_text(
            "def test_example():\n"
            "    assert True\n",
            encoding="utf-8",
        )

        subprocess.run(
            ["git", "init"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            ["git", "config", "user.email", "zeb@test.local"],
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
            ["git", "commit", "-m", "Initial acceptance fixture"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )

        self.runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={
                "filesystem.read",
                "git.read",
            },
        )

        self.assistant = Assistant(
            project_root=self.root,
            capability_runtime=self.runtime,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_project_info_establishes_controlled_workspace(self):
        result = self.assistant.execute_development("project_info")

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["workspace_root"],
            self.root.resolve().as_posix(),
        )
        self.assertIn("filesystem", result.data["capabilities"])
        self.assertIn("git", result.data["capabilities"])

    def test_list_exposes_workspace_contents(self):
        result = self.assistant.execute_development(
            "list",
            {"path": "."},
        )

        self.assertTrue(result.ok)

        names = {
            entry["name"]
            for entry in result.data["entries"]
        }

        self.assertIn("README.md", names)
        self.assertIn("modules", names)
        self.assertIn("tests", names)

    def test_read_exposes_selected_file(self):
        result = self.assistant.execute_development(
            "read",
            {"path": "README.md"},
        )

        self.assertTrue(result.ok)
        self.assertIn(
            "Controlled development interface.",
            result.data["content"],
        )

    def test_search_finds_content_inside_workspace(self):
        result = self.assistant.execute_development(
            "search",
            {"query": "zebra_bravo"},
        )

        self.assertTrue(result.ok)

        paths = {
            match["path"]
            for match in result.data["matches"]
        }

        self.assertIn("modules/example.py", paths)

    def test_git_status_reports_repository_state(self):
        result = self.assistant.execute_development("git_status")

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["operation"],
            "status",
        )
        self.assertIn(
            "## ",
            result.data["output"],
        )

    def test_git_log_reports_repository_history(self):
        result = self.assistant.execute_development(
            "git_log",
            {"limit": 1},
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["operation"],
            "log",
        )
        self.assertIn(
            "Initial acceptance fixture",
            result.data["output"],
        )

    def test_git_diff_reports_current_changes(self):
        changed_file = self.root / "README.md"

        changed_file.write_text(
            "# ZebraBravo\n\nModified through acceptance fixture.\n",
            encoding="utf-8",
        )

        result = self.assistant.execute_development("git_diff")

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["operation"],
            "diff",
        )
        self.assertIn(
            "Modified through acceptance fixture.",
            result.data["output"],
        )

    def test_development_interface_has_no_write_operation(self):
        result = self.assistant.execute_development(
            "write",
            {
                "path": "README.md",
                "content": "This must never be written.",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(
            result.code,
            "unsupported_operation",
        )

        self.assertNotIn(
            "write",
            self.assistant.development_interface._OPERATIONS,
        )

    def test_development_interface_respects_filesystem_permission(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"git.read"},
        )

        assistant = Assistant(
            project_root=self.root,
            capability_runtime=runtime,
        )

        result = assistant.execute_development(
            "read",
            {"path": "README.md"},
        )

        self.assertFalse(result.ok)
        self.assertEqual(
            result.code,
            "permission_denied",
        )

    def test_development_interface_respects_git_permission(self):
        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
        )

        assistant = Assistant(
            project_root=self.root,
            capability_runtime=runtime,
        )

        result = assistant.execute_development("git_status")

        self.assertFalse(result.ok)
        self.assertEqual(
            result.code,
            "permission_denied",
        )


if __name__ == "__main__":
    unittest.main()