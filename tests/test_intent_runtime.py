import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime
from intent.interpreter import IntentInterpreter


class IntentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)

        (self.workspace / "hello.txt").write_text(
            "Hello from Zoey.",
            encoding="utf-8",
        )

        self.interpreter = IntentInterpreter()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_intent_travels_through_runtime_to_filesystem(self):
        intent = self.interpreter.interpret(
            "read_file hello.txt"
        )

        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        result = runtime.execute(
            intent.capability,
            {
                "operation": intent.operation,
                **intent.parameters,
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

    def test_policy_can_block_interpreted_intent(self):
        intent = self.interpreter.interpret(
            "read_file hello.txt"
        )

        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions=set(),
        )

        result = runtime.execute(
            intent.capability,
            {
                "operation": intent.operation,
                **intent.parameters,
            },
        )

        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()