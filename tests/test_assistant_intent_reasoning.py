import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from assistant import Assistant


class StubReasoner:
    def reason(self, request):
        return {
            "name": "read_file",
            "capability": "filesystem",
            "operation": "read",
            "parameters": {"path": "README.txt"},
        }


class StubExecutor:
    def __init__(self):
        self.received = None

    def execute(self, intent):
        self.received = intent
        return {"ok": True}


def test_assistant_can_accept_an_intent_reasoner():
    executor = StubExecutor()

    assistant = Assistant(
        project_root=PROJECT_ROOT,
        intent_reasoner=StubReasoner(),
        intent_executor=executor,
    )

    assert assistant.intent_reasoner is not None

    reasoned = assistant.intent_reasoner.reason(
        "Please show me the README."
    )

    intent = assistant.form_intent(**reasoned)

    result = assistant.intent_executor.execute(intent)

    assert result["ok"] is True
    assert executor.received.name == "read_file"
    assert executor.received.capability == "filesystem"
    assert executor.received.operation == "read"
    assert executor.received.parameters["path"] == "README.txt"
