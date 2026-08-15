from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Mapping, Protocol


if TYPE_CHECKING:
    from capabilities.context import CapabilityContext


@dataclass(frozen=True)
class CapabilityMetadata:
    name: str
    description: str
    version: str = "0.1.0"
    side_effect: str = "read"
    required_permissions: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self):
        object.__setattr__(self, "required_permissions", frozenset(self.required_permissions))


@dataclass(frozen=True)
class CapabilityResult:
    ok: bool
    data: object | None = None
    message: str = ""
    code: str = "ok"


class CapabilityError(Exception):
    def __init__(self, code, message, data=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


class InvalidCapabilityRequest(CapabilityError):
    def __init__(self, message, data=None):
        super().__init__("invalid_request", message, data)


class CapabilityPermissionDenied(CapabilityError):
    def __init__(self, message="Capability permission denied.", data=None):
        super().__init__("permission_denied", message, data)


class Capability(Protocol):
    metadata: CapabilityMetadata

    def execute(
        self,
        request: Mapping[str, object],
        context: "CapabilityContext",
    ) -> CapabilityResult:
        ...
