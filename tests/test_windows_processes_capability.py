import json
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "modules"))

from capabilities.context import CapabilityContext
from capabilities.plugins.windows_processes import WindowsProcessesCapability


def test_metadata_declares_read_only_permission():
    capability = WindowsProcessesCapability()

    assert capability.metadata.name == "windows_processes"
    assert capability.metadata.required_permissions == {
        "windows.processes.read"
    }
    assert capability.metadata.side_effect == "read"
    assert capability.metadata.operations == {"list"}


def test_inventory_requires_permission():
    capability = WindowsProcessesCapability()

    result = capability.execute(
        {"operation": "list"},
        CapabilityContext(),
    )

    assert result.ok is False
    assert result.code == "permission_denied"


def test_rejects_unsupported_operation_without_running_powershell():
    capability = WindowsProcessesCapability()

    with patch("capabilities.plugins.windows_processes.subprocess.run") as run:
        result = capability.execute(
            {"operation": "terminate"},
            CapabilityContext(permissions={"windows.processes.read"}),
        )

    assert result.ok is False
    assert result.code == "unsupported_operation"
    run.assert_not_called()


def test_inventory_returns_validated_process_records():
    capability = WindowsProcessesCapability()
    records = [
        {
            "process_id": 4321,
            "parent_process_id": 1000,
            "name": "example.exe",
            "executable_path": r"C:\Example\example.exe",
        },
        {
            "process_id": 4322,
            "parent_process_id": 4321,
            "name": "child.exe",
            "executable_path": None,
        },
    ]
    completed = Mock(
        returncode=0,
        stdout=json.dumps(records),
        stderr="",
    )

    with patch(
        "capabilities.plugins.windows_processes.subprocess.run",
        return_value=completed,
    ) as run:
        result = capability.execute(
            {"operation": "list"},
            CapabilityContext(permissions={"windows.processes.read"}),
        )

    assert result.ok is True
    assert result.data["process_count"] == 2
    assert result.data["processes"] == records
    assert result.data["read_only"] is True
    assert run.call_args.kwargs["timeout"] == 15


def test_inventory_rejects_invalid_json():
    capability = WindowsProcessesCapability()
    completed = Mock(returncode=0, stdout="not-json", stderr="")

    with patch(
        "capabilities.plugins.windows_processes.subprocess.run",
        return_value=completed,
    ):
        result = capability.execute(
            {"operation": "list"},
            CapabilityContext(permissions={"windows.processes.read"}),
        )

    assert result.ok is False
    assert result.code == "invalid_process_data"


def test_inventory_handles_timeout():
    capability = WindowsProcessesCapability()

    with patch(
        "capabilities.plugins.windows_processes.subprocess.run",
        side_effect=subprocess.TimeoutExpired("powershell.exe", 15),
    ):
        result = capability.execute(
            {"operation": "list"},
            CapabilityContext(permissions={"windows.processes.read"}),
        )

    assert result.ok is False
    assert result.code == "process_query_timeout"


def test_inventory_handles_powershell_failure():
    capability = WindowsProcessesCapability()
    completed = Mock(returncode=1, stdout="", stderr="access denied")

    with patch(
        "capabilities.plugins.windows_processes.subprocess.run",
        return_value=completed,
    ):
        result = capability.execute(
            {"operation": "list"},
            CapabilityContext(permissions={"windows.processes.read"}),
        )

    assert result.ok is False
    assert result.code == "process_query_failed"
