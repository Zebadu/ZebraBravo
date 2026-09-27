from typing import Mapping
import subprocess
import threading

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class PowerShellExecuteCapability:
    """Governed execution of bounded PowerShell commands."""

    metadata = CapabilityMetadata(
        name="powershell_execute",
        description="Execute a PowerShell command and return bounded structured output.",
        required_permissions=frozenset({"powershell.execute"}),
        side_effect="write",
    )

    _DEFAULT_TIMEOUT_SECONDS = 30
    _MAX_TIMEOUT_SECONDS = 300
    _DEFAULT_OUTPUT_LIMIT = 64 * 1024
    _MAX_OUTPUT_LIMIT = 1024 * 1024

    def execute(self, request, context):
        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Capability request must be a mapping.",
            )

        if "powershell.execute" not in context.permissions:
            return self._failure(
                "permission_denied",
                "PowerShell execute permission denied.",
            )

        operation = request.get("operation")

        if operation != "execute":
            return self._failure(
                "unsupported_operation",
                f"Unsupported PowerShell Execute operation: {operation}",
            )

        command = request.get("command")

        if not isinstance(command, str) or not command.strip():
            return self._failure(
                "invalid_request",
                "Command is a required text field.",
            )

        timeout_seconds = request.get(
            "timeout_seconds",
            self._DEFAULT_TIMEOUT_SECONDS,
        )

        stdout_limit = request.get(
            "stdout_limit",
            self._DEFAULT_OUTPUT_LIMIT,
        )

        stderr_limit = request.get(
            "stderr_limit",
            self._DEFAULT_OUTPUT_LIMIT,
        )

        if not self._valid_positive_number(timeout_seconds):
            return self._failure(
                "invalid_request",
                "timeout_seconds must be a positive number.",
            )

        if timeout_seconds > self._MAX_TIMEOUT_SECONDS:
            return self._failure(
                "invalid_request",
                f"timeout_seconds cannot exceed {self._MAX_TIMEOUT_SECONDS}.",
            )

        if not self._valid_positive_integer(stdout_limit):
            return self._failure(
                "invalid_request",
                "stdout_limit must be a positive integer.",
            )

        if stdout_limit > self._MAX_OUTPUT_LIMIT:
            return self._failure(
                "invalid_request",
                f"stdout_limit cannot exceed {self._MAX_OUTPUT_LIMIT}.",
            )

        if not self._valid_positive_integer(stderr_limit):
            return self._failure(
                "invalid_request",
                "stderr_limit must be a positive integer.",
            )

        if stderr_limit > self._MAX_OUTPUT_LIMIT:
            return self._failure(
                "invalid_request",
                f"stderr_limit cannot exceed {self._MAX_OUTPUT_LIMIT}.",
            )

        try:
            process = subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    command,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError:
            return self._failure(
                "powershell_unavailable",
                "Windows PowerShell could not be accessed.",
            )

        stdout_state = {"text": "", "truncated": False}
        stderr_state = {"text": "", "truncated": False}

        stdout_thread = threading.Thread(
            target=self._read_stream,
            args=(process.stdout, stdout_limit, stdout_state),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=self._read_stream,
            args=(process.stderr, stderr_limit, stderr_state),
            daemon=True,
        )

        stdout_thread.start()
        stderr_thread.start()

        timed_out = False

        try:
            process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait()

        stdout_thread.join()
        stderr_thread.join()

        data = {
            "operation": "execute",
            "command": command,
            "stdout": stdout_state["text"],
            "stderr": stderr_state["text"],
            "returncode": process.returncode,
            "timed_out": timed_out,
            "stdout_truncated": stdout_state["truncated"],
            "stderr_truncated": stderr_state["truncated"],
        }

        if timed_out:
            return CapabilityResult(
                ok=False,
                data=data,
                message="PowerShell command timed out.",
                code="timeout",
            )

        if process.returncode != 0:
            return CapabilityResult(
                ok=False,
                data=data,
                message="PowerShell command failed.",
                code="powershell_failed",
            )

        return CapabilityResult(
            ok=True,
            data=data,
        )

    @staticmethod
    def _read_stream(stream, limit, state):
        if stream is None:
            return

        chunks = []
        total = 0

        while True:
            chunk = stream.read(4096)

            if not chunk:
                break

            remaining = limit - total

            if remaining > 0:
                accepted = chunk[:remaining]
                chunks.append(accepted.decode("utf-8", errors="replace"))
                total += len(accepted)

            if len(chunk) > remaining:
                state["truncated"] = True

        state["text"] = "".join(chunks)

    @staticmethod
    def _valid_positive_number(value):
        return (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and value > 0
        )

    @staticmethod
    def _valid_positive_integer(value):
        return (
            not isinstance(value, bool)
            and isinstance(value, int)
            and value > 0
        )

    @staticmethod
    def _failure(code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )
