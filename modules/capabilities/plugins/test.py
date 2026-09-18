from pathlib import Path
import subprocess
from typing import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class TestCapability:
    """Governed execution of ZebraBravo's approved pytest suite."""

    metadata = CapabilityMetadata(
        name="test",
        description="Run the ZebraBravo pytest suite within the approved workspace.",
        required_permissions=frozenset({"test.run"}),
        side_effect="test",
    )

    _ALLOWED_OPERATIONS = frozenset({"pytest"})

    def execute(self, request, context):
        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Capability request must be a mapping.",
            )

        workspace_root = context.workspace_root

        if workspace_root is None:
            return self._failure(
                "context_required",
                "A workspace root is required.",
            )

        root = Path(workspace_root).resolve()

        if not root.is_dir():
            return self._failure(
                "context_required",
                "Workspace root must be an existing directory.",
            )

        operation = request.get("operation")

        if operation not in self._ALLOWED_OPERATIONS:
            return self._failure(
                "unsupported_operation",
                f"Unsupported test operation: {operation}",
            )

        try:
            completed = subprocess.run(
                [
                    str(root / ".venv" / "Scripts" / "python.exe"),
                    "-m",
                    "pytest",
                ],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError:
            return self._failure(
                "test_unavailable",
                "The ZebraBravo virtual-environment Python executable could not be accessed.",
            )

        return CapabilityResult(
            ok=completed.returncode == 0,
            data={
                "operation": operation,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            message=(
                "ZebraBravo test suite passed."
                if completed.returncode == 0
                else "ZebraBravo test suite failed."
            ),
            code="ok" if completed.returncode == 0 else "test_failed",
        )

    @staticmethod
    def _failure(code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )
