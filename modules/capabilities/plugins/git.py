from pathlib import Path
import subprocess
from typing import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class GitCapability:
    metadata = CapabilityMetadata(
        name="git",
        description="Read-only access to Git repository state within an approved workspace.",
        required_permissions=frozenset({"git.read"}),
    )

    _ALLOWED_OPERATIONS = frozenset({"status", "log", "diff"})

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

        try:
            root = Path(workspace_root).resolve()
        except OSError:
            return self._failure(
                "git_failed",
                "Workspace root could not be resolved.",
            )

        if not root.is_dir():
            return self._failure(
                "context_required",
                "Workspace root must be an existing directory.",
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
                f"Unsupported Git operation: {operation}",
            )

        try:
            if operation == "status":
                return self._status(root)

            if operation == "log":
                return self._log(root, request)

            return self._diff(root, request)

        except OSError:
            return self._failure(
                "git_failed",
                "Git operation failed.",
            )

    def _status(self, root):
        result = self._run_git(root, ["status", "--short", "--branch"])

        return CapabilityResult(
            ok=True,
            data={
                "operation": "status",
                "output": result,
            },
        )

    def _log(self, root, request):
        limit = request.get("limit", 5)

        if not isinstance(limit, int) or isinstance(limit, bool):
            return self._failure(
                "invalid_request",
                "Log limit must be an integer.",
            )

        if limit < 1 or limit > 50:
            return self._failure(
                "invalid_request",
                "Log limit must be between 1 and 50.",
            )

        output = self._run_git(
            root,
            [
                "log",
                f"-{limit}",
                "--oneline",
                "--decorate",
            ],
        )

        return CapabilityResult(
            ok=True,
            data={
                "operation": "log",
                "limit": limit,
                "output": output,
            },
        )

    def _diff(self, root, request):
        staged = request.get("staged", False)

        if not isinstance(staged, bool):
            return self._failure(
                "invalid_request",
                "Staged must be a boolean.",
            )

        args = ["diff"]

        if staged:
            args.append("--cached")

        output = self._run_git(root, args)

        return CapabilityResult(
            ok=True,
            data={
                "operation": "diff",
                "staged": staged,
                "output": output,
            },
        )

    def _run_git(self, root, arguments):
        completed = subprocess.run(
            ["git", *arguments],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if completed.returncode != 0:
            raise OSError(completed.stderr.strip() or "Git command failed.")

        return completed.stdout

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )