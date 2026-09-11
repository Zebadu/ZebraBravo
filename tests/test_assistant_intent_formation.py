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


class AssistantIntentFormationTests(unittest.TestCase):
    def test_assistant_exposes_intent_formation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            runtime = CapabilityRuntime(
                workspace_root=workspace,
                permissions={"filesystem.read"},
            )

            memory_service = Mock()

            assistant = Assistant(
                project_root=workspace,
                memory_service=memory_service,
                capability_runtime=runtime,
            )

            intent = assistant.form_intent(
                name="read_file",
                capability="filesystem",
                operation="read",
                parameters={"path": "hello.txt"},
            )

            self.assertEqual(intent.name, "read_file")
            self.assertEqual(intent.capability, "filesystem")
            self.assertEqual(intent.operation, "read")
            self.assertEqual(
                intent.parameters,
                {"path": "hello.txt"},
            )
            self.assertEqual(intent.route, "capability")


if __name__ == "__main__":
    unittest.main()
