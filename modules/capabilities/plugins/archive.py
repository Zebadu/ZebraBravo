from pathlib import Path
from typing import Mapping
import zipfile

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class ArchiveCapability:
    metadata = CapabilityMetadata(
        name="archive",
        description="Read-only inspection of ZIP archives within an approved workspace.",
        required_permissions=frozenset({"archive.read"}),
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

        try:
            root = Path(workspace_root).resolve()
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

        operation = request.get("operation")
        path_text = request.get("path")

        if (
            not isinstance(operation, str)
            or not isinstance(path_text, str)
            or not path_text
        ):
            return self._failure(
                "invalid_request",
                "Operation and path are required text fields.",
            )

        if operation not in {"list", "read"}:
            return self._failure(
                "unsupported_operation",
                f"Unsupported archive operation: {operation}",
            )

        requested_path = Path(path_text)

        if requested_path.is_absolute():
            return self._failure(
                "invalid_request",
                "Absolute paths are not allowed.",
            )

        try:
            archive_path = (root / requested_path).resolve()
            archive_path.relative_to(root)
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

        if not archive_path.exists():
            return self._failure(
                "path_not_found",
                "Requested archive was not found.",
            )

        if not archive_path.is_file():
            return self._failure(
                "invalid_request",
                "Archive path must identify a file.",
            )

        if not zipfile.is_zipfile(archive_path):
            return self._failure(
                "invalid_archive",
                "Requested file is not a valid ZIP archive.",
            )

        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                if operation == "list":
                    return self._list(archive_path, root, archive)

                return self._read(archive_path, root, archive, request)

        except (OSError, zipfile.BadZipFile):
            return self._failure(
                "archive_failed",
                "Archive operation failed.",
            )

    def _list(self, archive_path, root, archive):
        members = []

        for info in sorted(
            archive.infolist(),
            key=lambda item: item.filename.lower(),
        ):
            kind = "directory" if info.is_dir() else "file"

            members.append(
                {
                    "name": info.filename,
                    "kind": kind,
                    "size": info.file_size,
                }
            )

        return CapabilityResult(
            ok=True,
            data={
                "path": self._relative_path(archive_path, root),
                "members": members,
            },
        )

    def _read(self, archive_path, root, archive, request):
        member = request.get("member")

        if not isinstance(member, str) or not member:
            return self._failure(
                "invalid_request",
                "A member path is required for read operations.",
            )

        member_path = Path(member)

        if member_path.is_absolute():
            return self._failure(
                "invalid_request",
                "Absolute member paths are not allowed.",
            )

        try:
            normalized_member = member_path.as_posix()

            if normalized_member.startswith("../") or normalized_member == "..":
                return self._failure(
                    "invalid_request",
                    "Archive member path must remain within the archive.",
                )

            if any(part == ".." for part in member_path.parts):
                return self._failure(
                    "invalid_request",
                    "Archive member path must remain within the archive.",
                )
        except OSError:
            return self._failure(
                "invalid_request",
                "Archive member path could not be resolved.",
            )

        try:
            info = archive.getinfo(normalized_member)
        except KeyError:
            return self._failure(
                "member_not_found",
                "Requested archive member was not found.",
            )

        if info.is_dir():
            return self._failure(
                "invalid_request",
                "Read operation requires a file member.",
            )

        try:
            content = archive.read(info).decode("utf-8")
        except UnicodeDecodeError:
            return self._failure(
                "unsupported_encoding",
                "Archive member is not valid UTF-8 text.",
            )

        return CapabilityResult(
            ok=True,
            data={
                "path": self._relative_path(archive_path, root),
                "member": normalized_member,
                "content": content,
            },
        )

    def _relative_path(self, path, root):
        relative_path = path.relative_to(root).as_posix()
        return relative_path or "."

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )