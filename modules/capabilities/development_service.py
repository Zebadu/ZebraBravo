from capabilities.development import DevelopmentInterface
from capabilities.development_protocol import DevelopmentProtocol
from capabilities.development_transport import DevelopmentTransport


class DevelopmentService:
    """Assembles the controlled development access pathway."""

    def __init__(self, runtime):
        if runtime is None:
            raise TypeError("A capability runtime is required.")

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