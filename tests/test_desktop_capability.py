import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext
from capabilities.contracts import CapabilityResult
from capabilities.plugins.desktop import DesktopCapability


class FakeDesktopGateway:
    def __init__(self, result=None):
        self.result = result or CapabilityResult(
            ok=True,
            data="desktop-result",
        )
        self.requests = []

    def inspect(self):
        self.requests.append("inspect")
        return self.result

    def execute(self, request):
        self.requests.append(request)
        return self.result


def test_desktop_capability_has_expected_metadata():
    capability = DesktopCapability()

    assert capability.metadata.name == "desktop"
    assert capability.metadata.required_permissions == {"desktop.read"}
    assert capability.metadata.side_effect == "read"


def test_desktop_capability_requires_desktop_gateway():
    capability = DesktopCapability()
    context = CapabilityContext()

    result = capability.execute(
        {"operation": "inspect"},
        context,
    )

    assert result.ok is False
    assert result.code == "context_required"


def test_desktop_capability_delegates_request_to_gateway():
    capability = DesktopCapability()
    gateway = FakeDesktopGateway()
    context = CapabilityContext(
        dependencies={"desktop_gateway": gateway},
    )
    request = {"operation": "inspect"}

    result = capability.execute(request, context)

    assert result.ok is True
    assert result.data == "desktop-result"
    assert gateway.requests == [request]


def test_desktop_capability_returns_gateway_failure_unchanged():
    capability = DesktopCapability()
    expected = CapabilityResult(
        ok=False,
        code="desktop_unavailable",
        message="Desktop Gateway unavailable.",
    )
    gateway = FakeDesktopGateway(expected)
    context = CapabilityContext(
        dependencies={"desktop_gateway": gateway},
    )

    result = capability.execute(
        {"operation": "inspect"},
        context,
    )

    assert result is expected
    assert result.ok is False
    assert result.code == "desktop_unavailable"


def test_desktop_capability_metadata_is_read_only():
    capability = DesktopCapability()

    assert capability.metadata.side_effect == "read"