import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext  # noqa: E402
from capabilities.executor import CapabilityExecutor  # noqa: E402
from capabilities.plugins.git import GitCapability  # noqa: E402
from capabilities.registry import CapabilityRegistry  # noqa: E402


class GitCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        self._run_git(["init"])
        self._run_git(["config", "user.name", "ZebraBravo Test"])
        self._run_git(["config", "user.email", "zebrabravo-test@example.invalid"])

        (self.root / "tracked.txt").write_text(
            "initial content\n",
            encoding="utf-8",
        )

        self._run_git(["add", "tracked.txt"])
        self._run_git(["commit", "-m", "Initial test commit"])

        registry = CapabilityRegistry()
        registry.register(GitCapability())

        self.executor = CapabilityExecutor(registry)

        self.context = CapabilityContext(
            workspace_root=self.root,
            permissions={"git.read"},
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run_git(self, arguments):
        import subprocess

        completed = subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if completed.returncode != 0:
            raise RuntimeError(
                completed.stderr.strip() or "Git test setup failed."
            )

        return completed.stdout

    def execute(self, operation, **request):
        return self.executor.execute(
            "git",
            {
                "operation": operation,
                **request,
            },
            self.context,
        )

    def test_status_reports_repository_state(self):
        result = self.execute("status")

        self.assertTrue(result.ok)
        self.assertEqual(result.data["operation"], "status")
        self.assertIn("## master", result.data["output"])

    def test_log_reports_recent_commits(self):
        result = self.execute("log", limit=5)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["operation"], "log")
        self.assertEqual(result.data["limit"], 5)
        self.assertIn("Initial test commit", result.data["output"])

    def test_diff_reports_uncommitted_changes(self):
        (self.root / "tracked.txt").write_text(
            "changed content\n",
            encoding="utf-8",
        )

        result = self.execute("diff")

        self.assertTrue(result.ok)
        self.assertEqual(result.data["operation"], "diff")
        self.assertFalse(result.data["staged"])
        self.assertIn("changed content", result.data["output"])

    def test_staged_diff_reports_staged_changes(self):
        (self.root / "tracked.txt").write_text(
            "staged content\n",
            encoding="utf-8",
        )
        self._run_git(["add", "tracked.txt"])

        result = self.execute("diff", staged=True)

        self.assertTrue(result.ok)
        self.assertTrue(result.data["staged"])
        self.assertIn("staged content", result.data["output"])

    def test_unsupported_operation_is_rejected(self):
        result = self.execute("commit")

        self.assertEqual(result.code, "unsupported_operation")

    def test_arbitrary_command_is_not_accepted(self):
        result = self.execute(
            "status",
            command=["status", "--porcelain"],
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data["operation"], "status")
        self.assertNotIn("command", result.data)

    def test_log_limit_must_be_an_integer(self):
        result = self.execute("log", limit="5")

        self.assertEqual(result.code, "invalid_request")

    def test_log_limit_is_bounded(self):
        result = self.execute("log", limit=51)

        self.assertEqual(result.code, "invalid_request")

    def test_diff_staged_must_be_boolean(self):
        result = self.execute("diff", staged="yes")

        self.assertEqual(result.code, "invalid_request")

    def test_permission_is_required(self):
        denied_context = CapabilityContext(
            workspace_root=self.root,
        )

        result = self.executor.execute(
            "git",
            {"operation": "status"},
            denied_context,
        )

        self.assertEqual(result.code, "permission_denied")

    def test_workspace_context_is_required(self):
        context = CapabilityContext(
            permissions={"git.read"},
        )

        result = self.executor.execute(
            "git",
            {"operation": "status"},
            context,
        )

        self.assertEqual(result.code, "context_required")

    def test_non_repository_workspace_fails_safely(self):
        non_repo = Path(self.temp_dir.name) / "not-a-repository"
        non_repo.mkdir()

        context = CapabilityContext(
            workspace_root=non_repo,
            permissions={"git.read"},
        )

        result = self.executor.execute(
            "git",
            {"operation": "status"},
            context,
        )

        self.assertEqual(result.code, "git_failed")

    def test_invalid_request_type_is_rejected(self):
        result = self.executor.execute(
            "git",
            "status",
            self.context,
        )

        self.assertEqual(result.code, "invalid_request")