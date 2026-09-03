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
        if not isinstance(operation, str) or not operation:
            return self._failure(
                "invalid_request",
                "Operation is a required text field.",
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

        if operation in {"list", "read"}:
            return self._filesystem(operation, request)

        if operation == "write":
            return self._write(request)

        if operation == "search":
            return self._search(request)

        if operation in {"git_status", "git_log", "git_diff"}:
            return self._git(operation, request)

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

        result = self.runtime.execute(
            "filesystem",
            capability_request,
        )

        if not result.ok or operation != "read":
            return result

        context = self.runtime.context
        workspace_root = context.workspace_root

        provenance = {
            "workspace_root": (
                workspace_root.as_posix()
                if workspace_root is not None
                else None
            ),
            "path": result.data.get("path"),
        }

        git_result = self.runtime.execute(
            "git",
            {
                "operation": "log",
                "limit": 1,
            },
        )

        if git_result.ok:
            provenance["git_log"] = git_result.data.get("output", "")
        else:
            provenance["git_log"] = None
            provenance["git_error"] = {
                "code": git_result.code,
                "message": git_result.message,
            }

        data = dict(result.data)
        data["provenance"] = provenance

        return CapabilityResult(
            ok=result.ok,
            data=data,
            message=result.message,
            code=result.code,
        )

    def _write(self, request):
        return self.runtime.execute(
            "filesystem_write",
            dict(request),
        )

    def _search(self, request):
        query = request.get("query")
        path = request.get("path", ".")

        if not isinstance(query, str) or not query:
            return self._failure(
                "invalid_request",
                "Search query is a required text field.",
            )

        if not isinstance(path, str) or not path:
            return self._failure(
                "invalid_request",
                "Search path must be a non-empty text field.",
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

        mapping = {
            "git_status": "status",
            "git_log": "log",
            "git_diff": "diff",
        }

        capability_request["operation"] = mapping[operation]

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
