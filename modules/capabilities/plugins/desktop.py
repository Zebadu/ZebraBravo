from capabilities.contracts import CapabilityMetadata, CapabilityResult
from capabilities.visual_observation import VisualObservation


class DesktopCapability:
    metadata = CapabilityMetadata(
        name="desktop",
        description="Controlled access to ZebraBravo's Desktop Gateway.",
        required_permissions=frozenset({"desktop.read"}),
        side_effect="read",
    )

    def execute(self, request, context):
        desktop_gateway = context.get_dependency("desktop_gateway")

        if desktop_gateway is None:
            return CapabilityResult(
                ok=False,
                message="Desktop Gateway service is required.",
                code="context_required",
            )

        result = desktop_gateway.execute(request)

        if request.get("operation") == "capture" and result.ok:
            return CapabilityResult(
                ok=True,
                data=VisualObservation.from_capture(result.data),
            )

        return result