import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext
from capabilities.plugins.powershell_xray import PowerShellXRayCapability


def test_xray_has_expected_metadata():
    capability = PowerShellXRayCapability()

    assert capability.metadata.name == "powershell_xray"
    assert capability.metadata.required_permissions == {"powershell.read"}
    assert capability.metadata.side_effect == "read"


def test_xray_requires_powershell_read_permission():
    capability = PowerShellXRayCapability()

    context = CapabilityContext()

    result = capability.execute(
        {"operation": "version"},
        context,
    )

    assert result.ok is False
    assert result.code == "permission_denied"


def test_xray_rejects_unknown_operation():
    capability = PowerShellXRayCapability()

    context = CapabilityContext(
        permissions={"powershell.read"},
    )

    result = capability.execute(
        {"operation": "launch_missiles"},
        context,
    )

    assert result.ok is False
    assert result.code == "unsupported_operation"


def test_xray_requires_an_operation():
    capability = PowerShellXRayCapability()

    context = CapabilityContext(
        permissions={"powershell.read"},
    )

    result = capability.execute({}, context)

    assert result.ok is False
    assert result.code == "invalid_request"


def test_xray_environment_operation_returns_read_only_snapshot():
    capability = PowerShellXRayCapability()

    context = CapabilityContext(
        permissions={"powershell.read"},
    )

    result = capability.execute(
        {"operation": "environment"},
        context,
    )

    assert result.ok is True
    assert result.data["operation"] == "environment"
    assert result.data["powershell"] == "powershell.exe"
    assert isinstance(result.data["version"], str)
    assert isinstance(result.data["edition"], str)
    assert isinstance(result.data["clr_version"], str)