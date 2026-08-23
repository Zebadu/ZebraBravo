from typing import Mapping


class DevelopmentTransport:
    """Transport-agnostic adapter for the ZebraBravo development protocol."""

    def __init__(self, protocol):
        if protocol is None:
            raise TypeError("A development protocol is required.")

        if not hasattr(protocol, "handle"):
            raise TypeError(
                "Development protocol must provide a handle method."
            )

        self.protocol = protocol

    def handle(self, request):
        """Pass a structured request to the development protocol."""

        if not isinstance(request, Mapping):
            return {
                "ok": False,
                "version": "1",
                "request_id": None,
                "operation": None,
                "code": "invalid_request",
                "message": "Transport request must be a mapping.",
            }

        return self.protocol.handle(request)