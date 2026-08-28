import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext  # noqa: E402
from capabilities.contracts import CapabilityResult  # noqa: E402
from capabilities.plugins.visual import VisualCapability  # noqa: E402


class FakeVisualGateway:
    def __init__(self, result=None):
        self.result = result or CapabilityResult(
            ok=True,
            data="visual-result",
        )
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return self.result


def test_visual_capability_has_expected_metadata():
    capability = VisualCapability()

    assert capability.metadata.name == "visual"
    assert capability.metadata.required_permissions == {"visual.read"}
    assert capability.metadata.side_effect == "read"


def test_visual_capability_requires_visual_gateway():
    capability = VisualCapability()
    context = CapabilityContext()

    result = capability.execute(
        {"operation": "list_assets"},
        context,
    )

    assert result.ok is False
    assert result.code == "context_required"


def test_visual_capability_delegates_request_to_gateway():
    capability = VisualCapability()
    gateway = FakeVisualGateway()
    context = CapabilityContext(
        dependencies={"visual_gateway": gateway},
    )
    request = {"operation": "list_assets"}

    result = capability.execute(request, context)

    assert result.ok is True
    assert result.data == "visual-result"
    assert gateway.requests == [request]


def test_visual_capability_returns_gateway_failure_unchanged():
    capability = VisualCapability()
    expected = CapabilityResult(
        ok=False,
        code="asset_not_found",
        message="Visual asset not found.",
    )
    gateway = FakeVisualGateway(expected)
    context = CapabilityContext(
        dependencies={"visual_gateway": gateway},
    )

    result = capability.execute(
        {"operation": "get_asset", "asset_id": "missing"},
        context,
    )

    assert result is expected
    assert result.ok is False
    assert result.code == "asset_not_found"


def test_visual_capability_metadata_is_read_only():
    capability = VisualCapability()

    assert capability.metadata.side_effect == "read"
