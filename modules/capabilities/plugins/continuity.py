from typing import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class ContinuityCapability:
    metadata = CapabilityMetadata(
        name="continuity",
        description="Controlled read access to ZebraBravo's Continuity record.",
        required_permissions=frozenset({"continuity.read"}),
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