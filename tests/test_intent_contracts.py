import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from intent.contracts import Intent


class IntentContractTests(unittest.TestCase):
    def test_intent_stores_action_description(self):
        intent = Intent(
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

    def test_intent_is_immutable(self):
        intent = Intent(
            name="read_file",
            capability="filesystem",
            operation="read",
            parameters={"path": "hello.txt"},
        )

        with self.assertRaises(AttributeError):
            intent.operation = "delete"


if __name__ == "__main__":
    unittest.main()