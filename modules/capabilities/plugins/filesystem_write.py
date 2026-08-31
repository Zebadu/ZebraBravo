from pathlib import Path
from typing import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class FileWriteCapability:
    metadata = CapabilityMetadata(
        name="filesystem_write",
        description="Controlled write access to files within an approved workspace.",
        side_effect="write",
        required_permissions=frozenset({"filesystem.write"}),
    )

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

        operation = request.get("operation")
        path_text = request.get("path")
        content = request.get("content")

        if (
            not isinstance(operation, str)
            or not operation
            or not isinstance(path_text, str)
            or not path_text
            or not isinstance(content, str)
        ):
            return self._failure(
                "invalid_request",
                "Operation, path, and content are required.",
            )

        if operation != "write":
            return self._failure(
                "unsupported_operation",
                f"Unsupported filesystem write operation: {operation}",
            )

        try:
            root = workspace_root.resolve()
        except OSError:
            return self._failure(
                "filesystem_failed",
                "Workspace root could not be resolved.",
            )

        if not root.is_dir():
            return self._failure(
                "context_required",
                "Workspace root must be an existing directory.",
            )

        requested_path = Path(path_text)

        if requested_path.is_absolute():
            return self._failure(
                "invalid_request",
                "Absolute paths are not allowed.",
            )

        try:
            path = (root / requested_path).resolve()
            path.relative_to(root)
        except ValueError:
            return self._failure(
                "invalid_request",
                "Path must remain within the workspace root.",
            )
        except OSError:
            return self._failure(
                "filesystem_failed",
                "Path could not be resolved.",
            )

        if path.exists() and not path.is_file():
            return self._failure(
                "invalid_request",
                "Write operation requires a file path.",
            )

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                content,
                encoding="utf-8",
            )
        except OSError:
            return self._failure(
                "filesystem_failed",
                "Filesystem write operation failed.",
            )

        return CapabilityResult(
            ok=True,
            data={
                "path": path.relative_to(root).as_posix(),
                "bytes_written": len(content.encode("utf-8")),
            },
        )

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )