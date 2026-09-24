from pathlib import Path
import subprocess
import tempfile
from typing import Mapping
import xml.etree.ElementTree as ET

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

        report_path = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".xml",
                delete=False,
            ) as report_file:
                report_path = Path(report_file.name)

            try:
                completed = subprocess.run(
                    [
                        str(root / ".venv" / "Scripts" / "python.exe"),
                        "-m",
                        "pytest",
                        f"--junit-xml={report_path}",
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

            try:
                verification = self._read_verification_report(report_path)
            except (OSError, ET.ParseError, ValueError) as exc:
                return CapabilityResult(
                    ok=False,
                    data={
                        "operation": operation,
                        "returncode": completed.returncode,
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                    },
                    message=f"JUnit verification report could not be read: {exc}",
                    code="verification_unavailable",
                )

            return CapabilityResult(
                ok=completed.returncode == 0,
                data={
                    "operation": operation,
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                    "verification": verification,
                },
                message=(
                    "ZebraBravo test suite passed."
                    if completed.returncode == 0
                    else "ZebraBravo test suite failed."
                ),
                code="ok" if completed.returncode == 0 else "test_failed",
            )
        except OSError:
            return self._failure(
                "verification_unavailable",
                "A temporary JUnit verification report could not be created.",
            )
        finally:
            if report_path is not None:
                report_path.unlink(missing_ok=True)

    @staticmethod
    def _read_verification_report(report_path):
        root = ET.parse(report_path).getroot()

        if root.tag == "testsuites":
            suite = root.find("testsuite")
        elif root.tag == "testsuite":
            suite = root
        else:
            raise ValueError("Unsupported JUnit report format.")

        if suite is None:
            raise ValueError("JUnit report contains no test suite.")

        return {
            "tests_total": int(suite.attrib.get("tests", 0)),
            "tests_passed": (
                int(suite.attrib.get("tests", 0))
                - int(suite.attrib.get("failures", 0))
                - int(suite.attrib.get("errors", 0))
                - int(suite.attrib.get("skipped", 0))
            ),
            "tests_failed": int(suite.attrib.get("failures", 0)),
            "tests_errors": int(suite.attrib.get("errors", 0)),
            "tests_skipped": int(suite.attrib.get("skipped", 0)),
        }

    @staticmethod
    def _failure(code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )
