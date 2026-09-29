from typing import Mapping

from capabilities.contracts import CapabilityResult


class VisualGateway:
    """Governed gateway for ZebraBravo's Triple Combo visual tools."""

    _ALLOWED_OPERATIONS = frozenset({"inspect"})

    def execute(self, request):
        if not isinstance(request, Mapping):
            return CapabilityResult(
                ok=False,
                message="Visual Gateway request must be a mapping.",
                code="invalid_request",
            )

        operation = request.get("operation")

        if operation not in self._ALLOWED_OPERATIONS:
            return CapabilityResult(
                ok=False,
                message=f"Unsupported visual operation: {operation}",
                code="unsupported_operation",
            )

        return CapabilityResult(
            ok=True,
            data={
                "operation": operation,
                "tools": {
                    "comfyui": "planned",
                    "blender": "planned",
                    "gimp": "planned",
                },
            },
            message="Visual Gateway inspection completed.",
            code="ok",
        )
