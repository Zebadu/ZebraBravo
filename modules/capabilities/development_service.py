from capabilities.contracts import CapabilityResult
from capabilities.development import DevelopmentInterface
from capabilities.development_protocol import DevelopmentProtocol
from capabilities.development_transport import DevelopmentTransport


class DevelopmentService:
    """Assembles the controlled development access pathway."""

    def __init__(self, runtime):
        if runtime is None:
            raise TypeError("A capability runtime is required.")

        self.runtime = runtime
        self.development_interface = DevelopmentInterface(runtime)
        self.protocol = DevelopmentProtocol(
            self.development_interface
        )
        self.transport = DevelopmentTransport(
            self.protocol
        )

    def handle(self, request):
        """Handle one structured development request."""

        return self.transport.handle(request)

    def set_development_mode(self, enabled):
        """Enable or disable governed development authorization."""

        if not isinstance(enabled, bool):
            return CapabilityResult(
                ok=False,
                message="Development mode must be a boolean.",
                code="invalid_request",
            )

        if enabled:
            self.runtime.development_authorization.enable()
        else:
            self.runtime.development_authorization.disable()

        return CapabilityResult(
            ok=True,
            data={
                "development_mode": self.runtime.development_authorization.enabled,
            },
            message=(
                "Zoey Development Mode enabled."
                if enabled
                else "Zoey Development Mode disabled."
            ),
        )

    def development_mode(self):
        """Return the current governed development authorization state."""

        return CapabilityResult(
            ok=True,
            data={
                "development_mode": self.runtime.development_authorization.enabled,
            },
        )
