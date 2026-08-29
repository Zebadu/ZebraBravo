from typing import Mapping
import subprocess

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class PowerShellXRayCapability:
    """Read-only visibility into the host PowerShell environment."""

    metadata = CapabilityMetadata(
        name="powershell_xray",
        description="Read-only visibility into the host PowerShell environment.",
        required_permissions=frozenset({"powershell.read"}),
        side_effect="read",
    )

    _ALLOWED_OPERATIONS = frozenset({"environment", "version"})

    def execute(self, request, context):
        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Capability request must be a mapping.",
            )

        if "powershell.read" not in context.permissions:
            return self._failure(
                "permission_denied",
                "PowerShell read permission denied.",
            )

        operation = request.get("operation")

        if not isinstance(operation, str) or not operation:
            return self._failure(
                "invalid_request",
                "Operation is a required text field.",
            )

        if operation not in self._ALLOWED_OPERATIONS:
            return self._failure(
                "unsupported_operation",
                f"Unsupported PowerShell X-Ray operation: {operation}",
            )

        if operation == "version":
            return self._version()

        if operation == "environment":
            return self._environment()

        return self._failure(
            "unsupported_operation",
            f"Unsupported PowerShell X-Ray operation: {operation}",
        )

    def _environment(self):
        script = (
            "$PSVersionTable.PSVersion.ToString(); "
            "$PSVersionTable.PSEdition; "
            "$PSVersionTable.CLRVersion.ToString()"
        )

        try:
            completed = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    script,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError:
            return self._failure(
                "powershell_unavailable",
                "Windows PowerShell could not be accessed.",
            )

        if completed.returncode != 0:
            return self._failure(
                "powershell_failed",
                "Windows PowerShell environment query failed.",
            )

        values = completed.stdout.splitlines()

        if len(values) < 3:
            return self._failure(
                "powershell_failed",
                "Windows PowerShell environment query returned incomplete data.",
            )

        version = values[0].strip()
        edition = values[1].strip()
        clr_version = values[2].strip()

        return CapabilityResult(
            ok=True,
            data={
                "operation": "environment",
                "powershell": "powershell.exe",
                "version": version,
                "edition": edition,
                "clr_version": clr_version,
            },
        )

    def _version(self):
        try:
            completed = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "$PSVersionTable.PSVersion.ToString()",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError:
            return self._failure(
                "powershell_unavailable",
                "Windows PowerShell could not be accessed.",
            )

        if completed.returncode != 0:
            return self._failure(
                "powershell_failed",
                "Windows PowerShell version query failed.",
            )

        version = completed.stdout.strip()

        return CapabilityResult(
            ok=True,
            data={
                "operation": "version",
                "version": version,
            },
        )

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )