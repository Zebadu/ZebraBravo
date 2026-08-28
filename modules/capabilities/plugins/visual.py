from capabilities.contracts import CapabilityMetadata, CapabilityResult


class VisualCapability:
    metadata = CapabilityMetadata(
        name="visual",
        description="Controlled access to ZebraBravo's Visual Gateway.",
        required_permissions=frozenset({"visual.read"}),
    )

    def execute(self, request, context):
        visual_gateway = context.get_dependency("visual_gateway")

        if visual_gateway is None:
            return CapabilityResult(
                ok=False,
                message="Visual Gateway service is required.",
                code="context_required",
            )

        return visual_gateway.execute(request)
