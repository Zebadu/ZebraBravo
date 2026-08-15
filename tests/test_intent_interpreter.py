import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from intent.interpreter import IntentInterpreter


class IntentInterpreterTests(unittest.TestCase):
    def setUp(self):
        self.interpreter = IntentInterpreter()

    def test_interpret_read_file_command(self):
        intent = self.interpreter.interpret(
            "read_file hello.txt"
        )

        self.assertEqual(intent.name, "read_file")
        self.assertEqual(intent.capability, "filesystem")
        self.assertEqual(intent.operation, "read")
        self.assertEqual(
            intent.parameters,
            {"path": "hello.txt"},
        )

    def test_empty_command_is_rejected(self):
        with self.assertRaises(ValueError):
            self.interpreter.interpret("")

    def test_unknown_command_is_rejected(self):
        with self.assertRaises(ValueError):
            self.interpreter.interpret("delete_everything")


if __name__ == "__main__":
    unittest.main()