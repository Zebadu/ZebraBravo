from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    from capabilities.context import CapabilityContext
    from capabilities.contracts import CapabilityMetadata


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    code: str
    message: str
    requires_confirmation: bool = False
    data: object | None = None


class CapabilityPolicy(Protocol):
    def evaluate(self, metadata: "CapabilityMetadata", request, context: "CapabilityContext") -> PolicyDecision:
        ...


class DefaultCapabilityPolicy:
    def __init__(self, allowed_capabilities=None, denied_capabilities=frozenset()):
        self.allowed_capabilities = (
            None if allowed_capabilities is None else frozenset(allowed_capabilities)
        )
        self.denied_capabilities = frozenset(denied_capabilities)

    def evaluate(self, metadata, request, context):
        if metadata.name in self.denied_capabilities:
            return PolicyDecision(
                allowed=False,
                code="capability_denied",
                message=f"Capability denied by policy: {metadata.name}",
            )

        if (
            self.allowed_capabilities is not None
            and metadata.name not in self.allowed_capabilities
        ):
            return PolicyDecision(
                allowed=False,
                code="capability_not_allowed",
                message=f"Capability is not allowed by policy: {metadata.name}",
            )

        if not metadata.required_permissions.issubset(context.permissions):
            return PolicyDecision(
                allowed=False,
                code="permission_denied",
                message="Capability permission denied.",
            )

        if metadata.side_effect == "read":
            return PolicyDecision(
                allowed=True,
                code="allowed",
                message="Capability allowed by read-only policy.",
            )

        if metadata.side_effect in {"write", "external"}:
            return PolicyDecision(
                allowed=False,
                code="confirmation_required",
                message="Capability requires future user confirmation.",
                requires_confirmation=True,
                data={"side_effect": metadata.side_effect},
            )

        return PolicyDecision(
            allowed=False,
            code="policy_invalid_metadata",
            message=f"Unsupported capability side effect: {metadata.side_effect}",
        )
