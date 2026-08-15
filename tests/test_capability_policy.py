import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext  # noqa: E402
from capabilities.contracts import CapabilityMetadata, CapabilityResult  # noqa: E402
from capabilities.executor import CapabilityExecutor  # noqa: E402
from capabilities.policy import DefaultCapabilityPolicy, PolicyDecision  # noqa: E402
from capabilities.policy_gateway import PolicyCapabilityGateway  # noqa: E402
from capabilities.registry import CapabilityRegistry  # noqa: E402


class FakeCapability:
    def __init__(self, name, side_effect="read", required_permissions=frozenset()):
        self.metadata = CapabilityMetadata(
            name=name,
            description=f"Fake {name} capability.",
            side_effect=side_effect,
            required_permissions=required_permissions,
        )
        self.executions = 0

    def execute(self, request, context):
        self.executions += 1
        return CapabilityResult(ok=True, data={"capability": self.metadata.name})


class PermissivePolicy:
    def evaluate(self, metadata, request, context):
        return PolicyDecision(True, "allowed", "Allowed by test policy.")


class CapabilityPolicyGatewayTests(unittest.TestCase):
    def setUp(self):
        self.registry = CapabilityRegistry()
        self.executor = CapabilityExecutor(self.registry)
        self.policy = DefaultCapabilityPolicy()
        self.gateway = PolicyCapabilityGateway(self.registry, self.executor, self.policy)

    def register(self, capability):
        self.registry.register(capability)
        return capability

    def test_permitted_read_capability_executes(self):
        capability = self.register(
            FakeCapability("read", required_permissions=frozenset({"read.access"}))
        )
        context = CapabilityContext(permissions={"read.access"})

        result = self.gateway.execute("read", {}, context)

        self.assertTrue(result.ok)
        self.assertEqual(capability.executions, 1)

    def test_explicit_denial_prevents_execution(self):
        capability = self.register(FakeCapability("blocked"))
        gateway = PolicyCapabilityGateway(
            self.registry,
            self.executor,
            DefaultCapabilityPolicy(denied_capabilities={"blocked"}),
        )

        result = gateway.execute("blocked", {}, CapabilityContext())

        self.assertEqual(result.code, "capability_denied")
        self.assertEqual(capability.executions, 0)

    def test_missing_permissions_prevent_execution(self):
        capability = self.register(
            FakeCapability("restricted", required_permissions=frozenset({"restricted.use"}))
        )

        result = self.gateway.execute("restricted", {}, CapabilityContext())

        self.assertEqual(result.code, "permission_denied")
        self.assertEqual(capability.executions, 0)

    def test_write_requires_confirmation_without_execution(self):
        capability = self.register(FakeCapability("writer", side_effect="write"))

        result = self.gateway.execute("writer", {}, CapabilityContext())

        self.assertEqual(result.code, "confirmation_required")
        self.assertFalse(result.ok)
        self.assertEqual(capability.executions, 0)

    def test_external_requires_confirmation_without_execution(self):
        capability = self.register(FakeCapability("external", side_effect="external"))

        result = self.gateway.execute("external", {}, CapabilityContext())

        self.assertEqual(result.code, "confirmation_required")
        self.assertFalse(result.ok)
        self.assertEqual(capability.executions, 0)

    def test_unknown_capability_preserves_executor_result(self):
        result = self.gateway.execute("missing", {}, CapabilityContext())

        self.assertEqual(result.code, "capability_not_found")

    def test_invalid_metadata_prevents_execution(self):
        capability = self.register(FakeCapability("invalid", side_effect="unknown"))

        result = self.gateway.execute("invalid", {}, CapabilityContext())

        self.assertEqual(result.code, "policy_invalid_metadata")
        self.assertEqual(capability.executions, 0)

    def test_executor_remains_permission_defense_in_depth(self):
        capability = self.register(
            FakeCapability("restricted", required_permissions=frozenset({"restricted.use"}))
        )
        gateway = PolicyCapabilityGateway(self.registry, self.executor, PermissivePolicy())

        result = gateway.execute("restricted", {}, CapabilityContext())

        self.assertEqual(result.code, "permission_denied")
        self.assertEqual(capability.executions, 0)
