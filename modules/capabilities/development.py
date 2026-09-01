from typing import Mapping

from capabilities.contracts import CapabilityResult


class DevelopmentInterface:
    """Controlled orchestration interface for ZebraBravo development access."""

    _OPERATIONS = frozenset(
        {
            "project_info",
            "list",
            "read",
            "write",
            "search",
            "git_status",
            "git_log",
            "git_diff",
            "powershell_xray",
        }
    )

    def __init__(self, runtime):
        self.runtime = runtime

    def execute(self, operation, request=None):
        """Execute one approved development operation."""

        if not isinstance(operation, str) or not operation:
            return self._failure(
                "invalid_request",
                "Development operation is required.",
            )

        if operation not in self._OPERATIONS:
            return self._failure(
                "unsupported_operation",
                f"Unsupported development operation: {operation}",
            )

        if request is None:
            request = {}

        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Development request must be a mapping.",
            )

        if operation == "project_info":
            return self._project_info()

        if operation == "list":
            return self._filesystem(
                "list",
                request,
            )

        if operation == "read":
            return self._filesystem(
                "read",
                request,
            )

        if operation == "write":
            return self._write(request)

        if operation == "search":
            return self._search(request)

        if operation == "git_status":
            return self._git(
                "status",
                request,
            )

        if operation == "git_log":
            return self._git(
                "log",
                request,
            )

        if operation == "git_diff":
            return self._git(
                "diff",
                request,
            )

        return self._powershell_xray(request)

    def _project_info(self):
        context = self.runtime.context
        root = context.workspace_root

        if root is None:
            return self._failure(
                "context_required",
                "A workspace root is required.",
            )

        return CapabilityResult(
            ok=True,
            data={
                "workspace_root": root.as_posix(),
                "capabilities": self.runtime.capability_names(),
            },
        )

    def _filesystem(self, operation, request):
        capability_request = dict(request)
        capability_request["operation"] = operation

        return self.runtime.execute(
            "filesystem",
            capability_request,
        )

    def _write(self, request):
        capability_request = dict(request)
        capability_request["operation"] = "write"

        return self.runtime.execute(
            "filesystem_write",
            capability_request,
        )

    def _search(self, request):
        query = request.get("query")

        if not isinstance(query, str) or not query:
            return self._failure(
                "invalid_request",
                "Search query is required.",
            )

        path = request.get("path", ".")

        if not isinstance(path, str) or not path:
            return self._failure(
                "invalid_request",
                "Search path must be text.",
            )

        capability_request = dict(request)
        capability_request["operation"] = "search"
        capability_request["query"] = query
        capability_request["path"] = path

        return self.runtime.execute(
            "filesystem",
            capability_request,
        )

    def _git(self, operation, request):
        capability_request = dict(request)
        capability_request["operation"] = operation

        return self.runtime.execute(
            "git",
            capability_request,
        )

    def _powershell_xray(self, request):
        capability_request = dict(request)

        if "operation" not in capability_request:
            capability_request["operation"] = "environment"

        return self.runtime.execute(
            "powershell_xray",
            capability_request,
        )

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )