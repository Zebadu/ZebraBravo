from dataclasses import dataclass, field
from typing import Any, FrozenSet, Mapping


@dataclass(frozen=True)
class CapabilityMetadata:
    """Describes a capability and the governance requirements around it."""

    name: str
    description: str
    version: str = "0.1.0"
    side_effect: str = "read"
    required_permissions: FrozenSet[str] = field(default_factory=frozenset)
    operation_side_effects: Mapping[str, str] = field(default_factory=dict)
    operation_permissions: Mapping[str, FrozenSet[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class CapabilityRequest:
    """A normalized request sent to a capability."""

    operation: str
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CapabilityResult:
    """The structured result returned by a capability execution."""

    ok: bool
    data: object | None = None
    message: str = ""
    code: str = "ok"
    requires_confirmation: bool = False


class CapabilityError(Exception):
    """Base exception for capability execution failures."""

    def __init__(
        self,
        code: str = "capability_error",
        message: str = "",
        data: object | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


class InvalidCapabilityRequest(CapabilityError):
    """Raised when a capability request is invalid."""

    def __init__(
        self,
        message: str,
        data: object | None = None,
        code: str = "invalid_request",
    ):
        super().__init__(
            code=code,
            message=message,
            data=data,
        )


class CapabilityPermissionDenied(CapabilityError):
    """Raised when a capability lacks the required permission."""

    def __init__(
        self,
        message: str,
        data: object | None = None,
        code: str = "permission_denied",
    ):
        super().__init__(
            code=code,
            message=message,
            data=data,
        )
