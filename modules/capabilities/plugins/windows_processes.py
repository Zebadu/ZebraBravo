import json
import subprocess
from collections.abc import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class WindowsProcessesCapability:
    """Read-only inventory of Windows processes and parent relationships."""

    metadata = CapabilityMetadata(
        name="windows_processes",
        description=(
            "Read-only inventory of Windows processes, parent IDs, "
            "and executable paths when available."
        ),
        required_permissions=frozenset({"windows.processes.read"}),
        side_effect="read",
        operations=frozenset({"list"}),
    )

    _SCRIPT = r"""
$items = @(
    Get-CimInstance -ClassName Win32_Process `
        -Property ProcessId, ParentProcessId, Name, ExecutablePath `
        -ErrorAction Stop |
    Select-Object `
        @{Name='process_id'; Expression={[int]$_.ProcessId}},
        @{Name='parent_process_id'; Expression={[int]$_.ParentProcessId}},
        @{Name='name'; Expression={[string]$_.Name}},
        @{Name='executable_path'; Expression={
            if ([string]::IsNullOrWhiteSpace($_.ExecutablePath)) {
                $null
            } else {
                [string]$_.ExecutablePath
            }
        }}
)
ConvertTo-Json -InputObject $items -Depth 3 -Compress
"""

    def execute(self, request, context):
        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Capability request must be a mapping.",
            )

        if "windows.processes.read" not in context.permissions:
            return self._failure(
                "permission_denied",
                "Windows process read permission denied.",
            )

        operation = request.get("operation")
        if operation != "list":
            return self._failure(
                "unsupported_operation",
                "Supported Windows process operation: list.",
            )

        try:
            completed = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    self._SCRIPT,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=15,
            )
        except subprocess.TimeoutExpired:
            return self._failure(
                "process_query_timeout",
                "Windows process inventory exceeded its time limit.",
            )
        except OSError:
            return self._failure(
                "powershell_unavailable",
                "Windows process inventory could not access PowerShell.",
            )

        if completed.returncode != 0:
            return self._failure(
                "process_query_failed",
                "Windows process inventory query failed.",
            )

        try:
            processes = json.loads(completed.stdout)
        except (json.JSONDecodeError, TypeError):
            return self._failure(
                "invalid_process_data",
                "Windows returned invalid process inventory data.",
            )

        if isinstance(processes, dict):
            processes = [processes]

        if not isinstance(processes, list) or not all(
            isinstance(item, dict) for item in processes
        ):
            return self._failure(
                "invalid_process_data",
                "Windows returned an unexpected process inventory format.",
            )

        return CapabilityResult(
            ok=True,
            data={
                "operation": "list",
                "process_count": len(processes),
                "processes": processes,
                "read_only": True,
                "limitations": (
                    "Executable paths may be unavailable for protected "
                    "processes or when Windows restricts access. A missing "
                    "path is not proof that a process has no executable path."
                ),
            },
        )

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )
