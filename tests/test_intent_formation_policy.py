import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime
from intent.executor import IntentExecutor
from intent.formation import IntentFormation


class IntentFormationPolicyTests(unittest.TestCase):
    def test_formed_intent_is_blocked_without_permission(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "hello.txt").write_text(
                "This must not be read.",
                encoding="utf-8",
            )

            formation = IntentFormation()

            intent = formation.form(
                name="read_file",
                capability="filesystem",
                operation="read",
                parameters={"path": "hello.txt"},
            )

            runtime = CapabilityRuntime(
                workspace_root=workspace,
                permissions=set(),
            )

            executor = IntentExecutor(runtime)
            result = executor.execute(intent)

            self.assertFalse(result.ok)
            self.assertEqual(result.code, "permission_denied")


if __name__ == "__main__":
    unittest.main()