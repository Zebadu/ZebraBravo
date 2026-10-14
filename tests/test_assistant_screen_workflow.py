from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from assistant import Assistant
from capabilities.contracts import CapabilityResult


class FakeRuntime:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def execute(self, capability, request):
        self.calls.append((capability, request))
        return self.results.pop(0)


def make_assistant(runtime):
    return Assistant(
        project_root=PROJECT_ROOT,
        capability_runtime=runtime,
    )


def test_describe_screen_captures_then_interprets_with_provenance():
    observation = object()
    capture = CapabilityResult(
        ok=True,
        data=observation,
        message="captured",
    )
    interpretation = CapabilityResult(
        ok=True,
        data={
            "observation_id": "desktop-test-1",
            "provenance": "local_desktop_capture",
            "description": "A test desktop.",
        },
        message="described",
    )
    runtime = FakeRuntime([capture, interpretation])

    result = make_assistant(runtime).process_request("describe my screen")

    assert result is interpretation
    assert [call[0] for call in runtime.calls] == [
        "desktop",
        "vision_understanding",
    ]
    assert runtime.calls[0][1] == {"operation": "capture"}
    assert runtime.calls[1][1] == {
        "operation": "describe",
        "observation": observation,
    }


def test_describe_screen_stops_when_capture_fails():
    failure = CapabilityResult(
        ok=False,
        message="Desktop capture denied",
        code="permission_denied",
    )
    runtime = FakeRuntime([failure])

    result = make_assistant(runtime).process_request("describe my screen")

    assert result is failure
    assert [call[0] for call in runtime.calls] == ["desktop"]


def test_screen_request_matching_is_explicit():
    assistant = make_assistant(FakeRuntime([]))

    assert assistant.is_screen_description_request("describe my screen")
    assert assistant.is_screen_description_request("What's on the screen?")
    assert not assistant.is_screen_description_request("delete my files")
    assert not assistant.is_screen_description_request("show README.txt")
