from typing import Mapping
from uuid import uuid4

from capabilities.contracts import CapabilityResult
from capabilities.development import DevelopmentInterface


class DevelopmentProtocol:
    """Validated machine-facing protocol for controlled development access."""

    VERSION = "1"

    _OPERATIONS = frozenset(
        {
            "project_info",
            "list",
            "read",
            "search",
            "git_status",
            "git_log",
            "git_diff",
        }
    )

    def __init__(self, development_interface):
        if not isinstance(
            development_interface,
            DevelopmentInterface,
        ):
            raise TypeError(
                "DevelopmentProtocol requires a DevelopmentInterface."
            )

        self.development_interface = development_interface

    def handle(self, request):
        """Validate and execute one protocol request."""

        if not isinstance(request, Mapping):
            return self._failure(
                "invalid_request",
                "Protocol request must be a mapping.",
            )

        request_id = request.get("request_id")

        if request_id is None:
            request_id = self._new_request_id()

        if not isinstance(request_id, str) or not request_id:
            return self._failure(
                "invalid_request",
                "Request ID must be non-empty text.",
                request_id=None,
            )

        version = request.get("version", self.VERSION)

        if version != self.VERSION:
            return self._failure(
                "unsupported_version",
                f"Unsupported protocol version: {version}",
                request_id=request_id,
            )

        operation = request.get("operation")

        if not isinstance(operation, str) or not operation:
            return self._failure(
                "invalid_request",
                "Operation is required.",
                request_id=request_id,
            )

        if operation not in self._OPERATIONS:
            return self._failure(
                "unsupported_operation",
                f"Unsupported development operation: {operation}",
                request_id=request_id,
            )

        payload = request.get("payload", {})

        if not isinstance(payload, Mapping):
            return self._failure(
                "invalid_request",
                "Request payload must be a mapping.",
                request_id=request_id,
            )

        result = self.development_interface.execute(
            operation,
            payload,
        )

        return self._response(
            request_id=request_id,
            operation=operation,
            result=result,
        )

    def _response(self, request_id, operation, result):
        return {
            "version": self.VERSION,
            "request_id": request_id,
            "operation": operation,
            "ok": result.ok,
            "data": result.data,
            "message": result.message,
            "code": result.code,
        }

    def _failure(self, code, message, request_id=None):
        return {
            "version": self.VERSION,
            "request_id": request_id,
            "operation": None,
            "ok": False,
            "data": None,
            "message": message,
            "code": code,
        }

    @staticmethod
    def _new_request_id():
        return uuid4().hex