from pathlib import Path
from typing import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class FileSystemCapability:
    metadata = CapabilityMetadata(
        name="filesystem",
        description="Read-only access to files within an approved workspace.",
        required_permissions=frozenset({"filesystem.read"}),
    )

    def execute(self, request, context):
        if not isinstance(request, Mapping):
            return self._failure("invalid_request", "Capability request must be a mapping.")

        workspace_root = context.workspace_root

        if workspace_root is None:
            return self._failure("context_required", "A workspace root is required.")

        try:
            root = Path(workspace_root).resolve()
        except OSError:
            return self._failure("filesystem_failed", "Workspace root could not be resolved.")

        if not root.is_dir():
            return self._failure("context_required", "Workspace root must be an existing directory.")

        operation = request.get("operation")
        path_text = request.get("path")

        if not isinstance(operation, str) or not isinstance(path_text, str) or not path_text:
            return self._failure("invalid_request", "Operation and path are required text fields.")

        if operation not in {"list", "read", "stat"}:
            return self._failure("unsupported_operation", f"Unsupported filesystem operation: {operation}")

        requested_path = Path(path_text)

        if requested_path.is_absolute():
            return self._failure("invalid_request", "Absolute paths are not allowed.")

        try:
            path = (root / requested_path).resolve()
            path.relative_to(root)
        except ValueError:
            return self._failure("invalid_request", "Path must remain within the workspace root.")
        except OSError:
            return self._failure("filesystem_failed", "Path could not be resolved.")

        if not path.exists():
            return self._failure("path_not_found", "Requested path was not found.")

        try:
            if operation == "list":
                return self._list(path, root)

            if operation == "read":
                return self._read(path, root)

            return self._stat(path, root)
        except OSError:
            return self._failure("filesystem_failed", "Filesystem operation failed.")

    def _list(self, path, root):
        if not path.is_dir():
            return self._failure("invalid_request", "List operation requires a directory.")

        entries = []

        for entry in sorted(path.iterdir(), key=lambda item: item.name.lower()):
            entries.append(
                {
                    "name": entry.name,
                    "path": entry.relative_to(root).as_posix(),
                    "kind": self._kind(entry),
                }
            )

        return CapabilityResult(
            ok=True,
            data={"path": self._relative_path(path, root), "entries": entries},
        )

    def _read(self, path, root):
        if not path.is_file():
            return self._failure("invalid_request", "Read operation requires a file.")

        return CapabilityResult(
            ok=True,
            data={
                "path": self._relative_path(path, root),
                "content": path.read_text(encoding="utf-8"),
            },
        )

    def _stat(self, path, root):
        stat = path.stat()

        return CapabilityResult(
            ok=True,
            data={
                "path": self._relative_path(path, root),
                "kind": self._kind(path),
                "size": stat.st_size,
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
            },
        )

    def _relative_path(self, path, root):
        relative_path = path.relative_to(root).as_posix()
        return relative_path or "."

    def _kind(self, path):
        if path.is_symlink():
            return "symlink"

        if path.is_dir():
            return "directory"

        if path.is_file():
            return "file"

        return "other"

    def _failure(self, code, message):
        return CapabilityResult(ok=False, message=message, code=code)
