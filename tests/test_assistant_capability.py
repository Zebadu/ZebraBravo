import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from assistant import Assistant
from capabilities.runtime import CapabilityRuntime


class AssistantCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)

        (self.workspace / "hello.txt").write_text(
            "Hello from Zoey.",
            encoding="utf-8",
        )

        notes_dir = self.workspace / "notes"
        notes_dir.mkdir()

        (notes_dir / "quest.txt").write_text(
            "The Quest for Truth continues.",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_assistant_can_receive_capability_runtime(self):
        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        memory_service = Mock()

        assistant = Assistant(
            project_root=self.workspace,
            memory_service=memory_service,
            capability_runtime=runtime,
        )

        result = assistant.execute_capability(
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
                "content": "Hello from Zoey.",
            },
        )

    def test_read_file_command_travels_through_intent_execution_path(self):
        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        memory_service = Mock()

        assistant = Assistant(
            project_root=self.workspace,
            memory_service=memory_service,
            capability_runtime=runtime,
        )

        output = io.StringIO()

        with redirect_stdout(output):
            result = assistant.process_command(
                "read_file hello.txt"
            )

        self.assertTrue(result)
        self.assertEqual(
            output.getvalue(),
            "Hello from Zoey.\n",
        )

    def test_read_file_command_is_blocked_without_permission(self):
        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions=set(),
        )

        memory_service = Mock()

        assistant = Assistant(
            project_root=self.workspace,
            memory_service=memory_service,
            capability_runtime=runtime,
        )

        output = io.StringIO()

        with redirect_stdout(output):
            result = assistant.process_command(
                "read_file hello.txt"
            )

        self.assertTrue(result)
        self.assertEqual(
            output.getvalue(),
            "Capability permission denied.\n",
        )

    def test_assistant_exposes_development_interface(self):
        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        memory_service = Mock()

        assistant = Assistant(
            project_root=self.workspace,
            memory_service=memory_service,
            capability_runtime=runtime,
        )

        result = assistant.execute_development(
            "project_info"
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["workspace_root"],
            self.workspace.as_posix(),
        )

    def test_assistant_development_read_travels_through_runtime(self):
        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        memory_service = Mock()

        assistant = Assistant(
            project_root=self.workspace,
            memory_service=memory_service,
            capability_runtime=runtime,
        )

        result = assistant.execute_development(
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
            "Hello from Zoey.",
        )
        self.assertEqual(
            result.data["provenance"]["workspace_root"],
            self.workspace.as_posix(),
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
            "permission_denied",
        )

    def test_assistant_development_search_travels_through_runtime(self):
        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        memory_service = Mock()

        assistant = Assistant(
            project_root=self.workspace,
            memory_service=memory_service,
            capability_runtime=runtime,
        )

        result = assistant.execute_development(
            "search",
            {
                "query": "Quest",
            },
        )

        self.assertTrue(result.ok)
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

    def test_assistant_development_respects_permission_boundary(self):
        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions=set(),
        )

        memory_service = Mock()

        assistant = Assistant(
            project_root=self.workspace,
            memory_service=memory_service,
            capability_runtime=runtime,
        )

        result = assistant.execute_development(
            "read",
            {
                "path": "hello.txt",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(
            result.code,
            "permission_denied",
        )


if __name__ == "__main__":
    unittest.main()