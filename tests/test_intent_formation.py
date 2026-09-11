import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from intent.formation import IntentFormation


class IntentFormationTests(unittest.TestCase):
    def setUp(self):
        self.formation = IntentFormation()

    def test_formation_creates_valid_capability_intent(self):
        intent = self.formation.form(
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
from intent.formation import IntentFormation


def test_formation_rejects_invalid_route():
    formation = IntentFormation()

    try:
        formation.form(
            name="test",
            capability="filesystem",
            operation="read",
            parameters={},
            route="invalid",
        )
    except ValueError:
        return

    raise AssertionError("Invalid intent route was accepted")
