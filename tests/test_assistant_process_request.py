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
    def execute(self, intent):
        return {
            "ok": True,
            "intent_name": intent.name,
            "path": intent.parameters["path"],
        }


def test_assistant_process_request_returns_structured_result():
    assistant = Assistant(
        project_root=PROJECT_ROOT,
        intent_reasoner=StubReasoner(),
        intent_executor=StubExecutor(),
    )

    result = assistant.process_request(
        "Please show me the README."
    )

    assert result["ok"] is True
    assert result["intent_name"] == "read_file"
    assert result["path"] == "README.txt"
