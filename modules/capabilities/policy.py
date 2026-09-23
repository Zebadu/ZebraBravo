from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    code: str
    message: str
    requires_confirmation: bool = False
    data: object | None = None

class CapabilityPolicy(Protocol):
    def evaluate(self, metadata, request, context) -> PolicyDecision:
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
                False,
                "capability_denied",
                f"Capability denied by policy: {metadata.name}",
            )

        if (
            self.allowed_capabilities is not None
            and metadata.name not in self.allowed_capabilities
        ):
            return PolicyDecision(
                False,
                "capability_not_allowed",
                f"Capability is not allowed by policy: {metadata.name}",
            )

        operation = getattr(request, "operation", None)
        if operation is None and isinstance(request, dict):
            operation = request.get("operation")

        operation_permissions = metadata.operation_permissions.get(
            operation,
            frozenset(),
        )
        effective_permissions = (
            metadata.required_permissions | operation_permissions
        )

        if not effective_permissions.issubset(context.permissions):
            return PolicyDecision(
                False,
                "permission_denied",
                "Capability permission denied.",
            )

        side_effect = metadata.operation_side_effects.get(
            operation,
            metadata.side_effect,
        )

        if side_effect == "read":
            return PolicyDecision(
                True,
                "allowed",
                "Capability allowed by read-only policy.",
            )

        if side_effect == "write":
            authorization = context.get_dependency("development_authorization")
            if authorization is not None and authorization.enabled:
                return PolicyDecision(
                    True,
                    "development_mode_allowed",
                    "Write capability allowed by active Development Mode.",
                )
            return PolicyDecision(
                False,
                "confirmation_required",
                "Capability requires active Development Mode.",
                True,
                {"side_effect": side_effect},
            )

        if side_effect == "test":
            authorization = context.get_dependency("development_authorization")
            if authorization is not None and authorization.enabled:
                return PolicyDecision(
                    True,
                    "development_mode_allowed",
                    "Test capability allowed by active Development Mode.",
                )
            return PolicyDecision(
                False,
                "confirmation_required",
                "Test capability requires active Development Mode.",
                True,
                {"side_effect": side_effect},
            )

        if side_effect == "external":
            return PolicyDecision(
                False,
                "confirmation_required",
                "External capability requires explicit confirmation.",
                True,
                {"side_effect": side_effect},
            )

        return PolicyDecision(
            False,
            "policy_invalid_metadata",
            f"Unsupported capability side effect: {side_effect}",
        )
