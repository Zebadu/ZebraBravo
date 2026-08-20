from typing import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult


class TruthCapability:
    metadata = CapabilityMetadata(
        name="truth",
        description="Controlled access to ZebraBravo's Truth Gate.",
        required_permissions=frozenset({"truth.read"}),
    )

    def execute(self, request, context):
        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Capability request must be a mapping.",
            )

        truth_gate = context.get_dependency("truth_gate")

        if truth_gate is None:
            return self._failure(
                "context_required",
                "Truth Gate service is required.",
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
                data=truth_gate.get_current(),
            )

        if operation == "get_claim":
            claim_id = request.get("claim_id")

            if not isinstance(claim_id, str) or not claim_id:
                return self._failure(
                    "invalid_request",
                    "Claim ID is required.",
                )

            try:
                claim = truth_gate.get_claim(claim_id)
            except ValueError as error:
                return self._failure(
                    "claim_not_found",
                    str(error),
                )

            return CapabilityResult(
                ok=True,
                data=claim,
            )

        return self._failure(
            "unsupported_operation",
            f"Unsupported truth operation: {operation}",
        )

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )