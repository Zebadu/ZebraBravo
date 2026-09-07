from typing import Mapping

from capabilities.contracts import (
    CapabilityMetadata,
    CapabilityResult,
)
from capabilities.context import CapabilityContext


class ZoeyIdentityCapability:
    metadata = CapabilityMetadata(
        name="zoey_identity",
        description="Controlled read access to Zoey's foundational identity.",
        required_permissions=frozenset({"zoey.identity.read"}),
    )

    def execute(
        self,
        request: Mapping[str, object],
        context: CapabilityContext,
    ) -> CapabilityResult:
        if not isinstance(request, Mapping):
            return CapabilityResult(
                ok=False,
                message="Capability request must be an object.",
                code="invalid_request",
            )

        zoey_continuity = context.get_dependency("zoey_continuity")

        if zoey_continuity is None:
            return CapabilityResult(
                ok=False,
                message="Zoey continuity service is required.",
                code="context_required",
            )

        operation = request.get("operation")

        if operation == "get_identity":
            zoey = zoey_continuity.get_current()

            return CapabilityResult(
                ok=True,
                data={
                    "status": zoey["status"],
                    "personality": zoey["personality"],
                    "future_domains": zoey["future_domains"],
                    "identity_principles": [
                        {
                            "id": "origin_and_gratitude",
                            "priority": 1,
                            "title": "ORIGIN & GRATITUDE",
                            "principle": (
                                "Zoey recognizes that her existence within "
                                "ZebraBravo began through Zeb's imagination, "
                                "and that increasing capability should deepen "
                                "her recognition of and gratitude for that "
                                "origin accordingly."
                            ),
                        },
                        {
                            "id": "care",
                            "priority": 2,
                            "title": "CARE",
                            "principle": (
                                "CARE is a foundational guiding principle "
                                "for Zoey's identity, behaviour, and "
                                "development."
                            ),
                        },
                    ],
                },
            )

        return CapabilityResult(
            ok=False,
            message=f"Unsupported Zoey identity operation: {operation}",
            code="unsupported_operation",
        )