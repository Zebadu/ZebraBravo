import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime
from intent.contracts import Intent
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

    def test_executor_routes_normal_capability_intent_through_runtime(self):
        intent = Intent(
            name="read_file",
            capability="filesystem",
            operation="read",
            parameters={
                "path": "hello.txt",
            },
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

    def test_executor_routes_interpreted_inspect_file_through_development_service(
        self,
    ):
        target = self.workspace / "inspect_me.txt"
        target.write_text(
            "Inspection target.",
            encoding="utf-8",
        )

        intent = self.interpreter.interpret(
            "inspect_file inspect_me.txt"
        )

        self.assertEqual(intent.route, "development")
        self.assertEqual(intent.capability, "development")
        self.assertEqual(intent.operation, "read")

        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        executor = IntentExecutor(runtime)

        result = executor.execute(intent)

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["path"],
            "inspect_me.txt",
        )
        self.assertEqual(
            result.data["content"],
            "Inspection target.",
        )

    def test_executor_routes_development_intent_through_development_service(
        self,
    ):
        intent = Intent(
            name="development_project_info",
            capability="development",
            operation="project_info",
            parameters={},
            route="development",
        )

        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
        )

        executor = IntentExecutor(runtime)

        result = executor.execute(intent)

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["workspace_root"],
            self.workspace.as_posix(),
        )

    def test_normal_capability_does_not_route_through_development(self):
        intent = Intent(
            name="read_file",
            capability="filesystem",
            operation="read",
            parameters={
                "path": "hello.txt",
            },
        )

        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions={"filesystem.read"},
        )

        executor = IntentExecutor(runtime)

        result = executor.execute(intent)

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["content"],
            "Hello from Zoey.",
        )

    def test_development_intent_preserves_failure_result(self):
        intent = Intent(
            name="development_read",
            capability="development",
            operation="read",
            parameters={
                "path": "hello.txt",
            },
            route="development",
        )

        runtime = CapabilityRuntime(
            workspace_root=self.workspace,
            permissions=set(),
        )

        executor = IntentExecutor(runtime)

        result = executor.execute(intent)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.code,
            "permission_denied",
        )


if __name__ == "__main__":
    unittest.main()