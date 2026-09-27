import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext
from capabilities.plugins.powershell_execute import PowerShellExecuteCapability


def test_execute_has_expected_metadata():
    capability = PowerShellExecuteCapability()

    assert capability.metadata.name == "powershell_execute"
    assert capability.metadata.required_permissions == {"powershell.execute"}
    assert capability.metadata.side_effect == "write"


def test_execute_requires_powershell_execute_permission():
    capability = PowerShellExecuteCapability()

    context = CapabilityContext()

    result = capability.execute(
        {"operation": "execute", "command": "Write-Output 'hello'"},
        context,
    )

    assert result.ok is False
    assert result.code == "permission_denied"


def test_execute_requires_a_command():
    capability = PowerShellExecuteCapability()

    context = CapabilityContext(
        permissions={"powershell.execute"},
    )

    result = capability.execute(
        {"operation": "execute"},
        context,
    )

    assert result.ok is False
    assert result.code == "invalid_request"


def test_execute_returns_structured_command_result():
    capability = PowerShellExecuteCapability()

    context = CapabilityContext(
        permissions={"powershell.execute"},
    )

    result = capability.execute(
        {
            "operation": "execute",
            "command": "Write-Output 'ZEBRABRAVO_EXECUTION_PROOF'",
        },
        context,
    )

    assert result.ok is True
    assert result.data["operation"] == "execute"
    assert result.data["stdout"].strip() == "ZEBRABRAVO_EXECUTION_PROOF"
    assert result.data["stderr"] == ""
    assert result.data["returncode"] == 0
    assert result.data["timed_out"] is False
    assert result.data["stdout_truncated"] is False
    assert result.data["stderr_truncated"] is False

def test_execute_truncates_stdout_at_requested_limit():
    capability = PowerShellExecuteCapability()

    context = CapabilityContext(
        permissions={"powershell.execute"},
    )

    result = capability.execute(
        {
            "operation": "execute",
            "command": "Write-Output ('X' * 1000)",
            "stdout_limit": 100,
        },
        context,
    )

    assert result.ok is True
    assert len(result.data["stdout"]) <= 100
    assert result.data["stdout_truncated"] is True


def test_execute_truncates_stderr_at_requested_limit():
    capability = PowerShellExecuteCapability()

    context = CapabilityContext(
        permissions={"powershell.execute"},
    )

    result = capability.execute(
        {
            "operation": "execute",
            "command": "[Console]::Error.Write(('E' * 1000))",
            "stderr_limit": 100,
        },
        context,
    )

    assert result.ok is True
    assert len(result.data["stderr"]) <= 100
    assert result.data["stderr_truncated"] is True


def test_execute_times_out_long_running_command():
    capability = PowerShellExecuteCapability()

    context = CapabilityContext(
        permissions={"powershell.execute"},
    )

    result = capability.execute(
        {
            "operation": "execute",
            "command": "Start-Sleep -Seconds 10",
            "timeout_seconds": 1,
        },
        context,
    )

    assert result.ok is False
    assert result.code == "timeout"
    assert result.data["timed_out"] is True
