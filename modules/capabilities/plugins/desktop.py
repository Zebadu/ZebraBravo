from capabilities.contracts import CapabilityMetadata, CapabilityResult


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

        return desktop_gateway.execute(request)