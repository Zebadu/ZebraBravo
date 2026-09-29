import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from intent.simple_reasoner import SimpleIntentReasoner


def test_simple_reasoner_can_form_read_file_intent():
    reasoner = SimpleIntentReasoner()

    result = reasoner.reason("Please show me the README.")

    assert result == {
        "name": "read_file",
        "capability": "filesystem",
        "operation": "read",
        "parameters": {"path": "README"},
        "route": "capability",
    }
