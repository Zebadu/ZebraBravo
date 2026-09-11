import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from intent.reasoning import IntentReasoner


class StubReasoner:
    def reason(self, request):
        return {
            "name": "read_file",
            "capability": "filesystem",
            "operation": "read",
            "parameters": {"path": "README.txt"},
        }


def test_intent_reasoner_contract_accepts_structured_reasoning():
    reasoner: IntentReasoner = StubReasoner()

    result = reasoner.reason("Please show me the README.")

    assert result["name"] == "read_file"
    assert result["capability"] == "filesystem"
    assert result["operation"] == "read"
    assert result["parameters"]["path"] == "README.txt"
