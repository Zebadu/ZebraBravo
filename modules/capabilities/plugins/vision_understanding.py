from collections.abc import Mapping

from capabilities.contracts import CapabilityMetadata, CapabilityResult
from capabilities.visual_observation import VisualObservation


class VisionUnderstandingCapability:
    """Governed interpretation of visual observations through an injected provider."""

    metadata = CapabilityMetadata(
        name="vision_understanding",
        description="Interpret visual observations through a governed vision provider.",
        required_permissions=frozenset({"vision.interpret"}),
        side_effect="read",
        operations=frozenset({"describe"}),
    )

    def execute(self, request, context):
        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Capability request must be a mapping.",
            )

        operation = request.get("operation")

        if operation != "describe":
            return self._failure(
                "unsupported_operation",
                f"Unsupported vision operation: {operation}",
            )

        observation = request.get("observation")

        if not isinstance(observation, VisualObservation):
            return self._failure(
                "invalid_request",
                "A valid VisualObservation is required.",
            )

        provider = context.get_dependency("vision_provider")

        if provider is None:
            return self._failure(
                "context_required",
                "An injected vision provider is required.",
            )

        describe = getattr(provider, "describe", None)

        if not callable(describe):
            return self._failure(
                "invalid_provider",
                "Vision provider must implement describe(observation).",
            )

        try:
            description = describe(observation)
        except Exception:
            return self._failure(
                "vision_failed",
                "The vision provider could not interpret the observation.",
            )

        if not isinstance(description, str) or not description.strip():
            return self._failure(
                "invalid_provider_result",
                "Vision provider returned no valid description.",
            )

        return CapabilityResult(
            ok=True,
            data={
                "observation_id": observation.observation_id,
                "description": description.strip(),
                "provenance": observation.provenance,
            },
            message="Visual observation interpreted successfully.",
            code="ok",
        )

    @staticmethod
    def _failure(code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )
