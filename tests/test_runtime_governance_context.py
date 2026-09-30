import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.contracts import CapabilityMetadata, CapabilityResult
from capabilities.governance import GovernanceContext
from capabilities.runtime import CapabilityRuntime


class RuntimeGovernanceContextTests(unittest.TestCase):
    def test_runtime_preserves_supplied_governance_context(self):
        governance = GovernanceContext(
            principal="Zeb",
            authority="owner",
            mission_id="runtime-governance-integration",
            resource_scope=("workspace", "desktop"),
            authorization_provenance={
                "source": "explicit_user_authorization",
                "session": "test",
            },
        )

        runtime = CapabilityRuntime(
            workspace_root=PROJECT_ROOT,
            permissions={"filesystem.read"},
            governance_context=governance,
        )

        self.assertIs(
            runtime.context.governance_context,
            governance,
        )

        self.assertEqual(
            runtime.context.governance_context.principal,
            "Zeb",
        )
        self.assertEqual(
            runtime.context.governance_context.authority,
            "owner",
        )
        self.assertEqual(
            runtime.context.governance_context.mission_id,
            "runtime-governance-integration",
        )
        self.assertEqual(
            runtime.context.governance_context.resource_scope,
            ("workspace", "desktop"),
        )
        self.assertEqual(
            dict(
                runtime.context.governance_context.authorization_provenance
            ),
            {
                "source": "explicit_user_authorization",
                "session": "test",
            },
        )


class ContextCaptureCapability:
    metadata = CapabilityMetadata(
        name="context_capture",
        description="Test capability for governance context propagation.",
        side_effect="read",
    )

    def execute(self, request, context):
        governance = context.governance_context

        return CapabilityResult(
            ok=True,
            data={
                "principal": governance.principal,
                "authority": governance.authority,
                "mission_id": governance.mission_id,
                "resource_scope": governance.resource_scope,
            },
        )


def test_runtime_propagates_governance_context_to_capability():
    governance = GovernanceContext(
        principal="Zeb",
        authority="owner",
        mission_id="governance-context-propagation",
        resource_scope=("zebrabravo",),
    )

    runtime = CapabilityRuntime(
        workspace_root=PROJECT_ROOT,
        governance_context=governance,
    )

    runtime.registry.register(ContextCaptureCapability())

    result = runtime.execute(
        "context_capture",
        {"operation": "inspect"},
    )

    assert result.ok
    assert result.data == {
        "principal": "Zeb",
        "authority": "owner",
        "mission_id": "governance-context-propagation",
        "resource_scope": ("zebrabravo",),
    }


class ContextCaptureCapability:
    metadata = CapabilityMetadata(
        name="context_capture",
        description="Test capability for governance context propagation.",
        side_effect="read",
    )

    def execute(self, request, context):
        governance = context.governance_context

        return CapabilityResult(
            ok=True,
            data={
                "principal": governance.principal,
                "authority": governance.authority,
                "mission_id": governance.mission_id,
                "resource_scope": governance.resource_scope,
            },
        )


def test_runtime_propagates_governance_context_to_capability():
    governance = GovernanceContext(
        principal="Zeb",
        authority="owner",
        mission_id="governance-context-propagation",
        resource_scope=("zebrabravo",),
    )

    runtime = CapabilityRuntime(
        workspace_root=PROJECT_ROOT,
        governance_context=governance,
    )

    runtime.registry.register(ContextCaptureCapability())

    result = runtime.execute(
        "context_capture",
        {"operation": "inspect"},
    )

    assert result.ok
    assert result.data == {
        "principal": "Zeb",
        "authority": "owner",
        "mission_id": "governance-context-propagation",
        "resource_scope": ("zebrabravo",),
    }


if __name__ == "__main__":
    unittest.main()
