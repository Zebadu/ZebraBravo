import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()