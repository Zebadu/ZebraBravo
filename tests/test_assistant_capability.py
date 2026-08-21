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


if __name__ == "__main__":
    unittest.main()