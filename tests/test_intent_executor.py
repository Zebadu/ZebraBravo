import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime
from intent.executor import IntentExecutor
from intent.interpreter import IntentInterpreter


class IntentExecutorTests(unittest.TestCase):
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

    def test_executor_sends_intent_through_runtime(self):
        intent = self.interpreter.interpret(
            "read_file hello.txt"
        )

        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        executor = IntentExecutor(runtime)

        result = executor.execute(intent)

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data,
            {
                "path": "hello.txt",
                "content": "Hello from Zoey.",
            },
        )

    def test_executor_preserves_runtime_policy_boundary(self):
        intent = self.interpreter.interpret(
            "read_file hello.txt"
        )

        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions=set(),
        )

        executor = IntentExecutor(runtime)

        result = executor.execute(intent)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "permission_denied")


if __name__ == "__main__":
    unittest.main()