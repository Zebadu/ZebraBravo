from pathlib import Path

from capabilities.context import CapabilityContext
from capabilities.executor import CapabilityExecutor
from capabilities.plugins.filesystem import FileSystemCapability
from capabilities.plugins.truth import TruthCapability
from capabilities.policy import DefaultCapabilityPolicy
from capabilities.policy_gateway import PolicyCapabilityGateway
from capabilities.registry import CapabilityRegistry


class CapabilityRuntime:
    """Assembles and exposes ZebraBravo's controlled capability pathway."""

    def __init__(
        self,
        workspace_root=None,
        permissions=(),
        allowed_capabilities=None,
        denied_capabilities=(),
        dependencies=None,
    ):
        self.registry = CapabilityRegistry()

        self.registry.register(FileSystemCapability())
        self.registry.register(TruthCapability())

        self.executor = CapabilityExecutor(self.registry)

        self.policy = DefaultCapabilityPolicy(
            allowed_capabilities=allowed_capabilities,
            denied_capabilities=denied_capabilities,
        )

        self.gateway = PolicyCapabilityGateway(
            self.registry,
            self.executor,
            self.policy,
        )

        self.context = CapabilityContext(
            workspace_root=(
                None
                if workspace_root is None
                else Path(workspace_root).resolve()
            ),
            dependencies=(
                {}
                if dependencies is None
                else dependencies
            ),
            permissions=frozenset(permissions),
        )

    def execute(self, capability_name, request):
        """Execute a capability request through policy and execution boundaries."""
        return self.gateway.execute(
            capability_name,
            request,
            self.context,
        )

    def capability_names(self):
        """Return the registered capability names."""
        return self.registry.names()