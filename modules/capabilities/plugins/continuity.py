from typing import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class ContinuityCapability:
    metadata = CapabilityMetadata(
        name="continuity",
        description="Controlled read access to ZebraBravo's Continuity record.",
        required_permissions=frozenset({"continuity.read"}),
        operation_side_effects={"get_current": "read", "update_checkpoint": "write"},
        operation_permissions={"update_checkpoint": frozenset({"continuity.write"})},
    )

    def execute(self, request, context):
        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Capability request must be a mapping.",
            )

        continuity = context.get_dependency("continuity")

        if continuity is None:
            return self._failure(
                "context_required",
                "Continuity service is required.",
            )

        operation = request.get("operation")

        if not isinstance(operation, str) or not operation:
            return self._failure(
                "invalid_request",
                "Operation is required.",
            )

        if operation == "update_checkpoint":
            if "continuity.write" not in context.permissions:
                return self._failure(
                    "permission_denied",
                    "Continuity write permission is required.",
                )

            checkpoint = request.get("checkpoint")
            if not isinstance(checkpoint, dict):
                return self._failure(
                    "invalid_request",
                    "Checkpoint must be an object.",
                )

            continuity.update_checkpoint(checkpoint)
            return CapabilityResult(
                ok=True,
                data={"operation": "update_checkpoint"},
            )

        if operation == "get_current":
            return CapabilityResult(
                ok=True,
                data=continuity.get_current(),
            )

        return self._failure(
            "unsupported_operation",
            f"Unsupported continuity operation: {operation}",
        )

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )

