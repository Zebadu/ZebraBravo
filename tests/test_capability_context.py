import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext
from capabilities.governance import GovernanceContext


class CapabilityContextTests(unittest.TestCase):
    def test_default_governance_context_is_safe_and_empty(self):
        context = CapabilityContext()

        self.assertEqual(context.governance_context.principal, "")
        self.assertEqual(context.governance_context.authority, "")
        self.assertEqual(context.governance_context.mission_id, "")
        self.assertEqual(context.governance_context.resource_scope, ())
        self.assertEqual(
            dict(context.governance_context.authorization_provenance),
            {},
        )

    def test_explicit_governance_context_is_preserved(self):
        governance = GovernanceContext(
            principal="Zeb",
            authority="owner",
            mission_id="governance-context-integration",
            resource_scope=("workspace", "desktop"),
            authorization_provenance={
                "source": "explicit_user_authorization",
            },
        )

        context = CapabilityContext(
            governance_context=governance,
        )

        self.assertIs(context.governance_context, governance)
        self.assertEqual(context.governance_context.principal, "Zeb")
        self.assertEqual(context.governance_context.authority, "owner")
        self.assertEqual(
            context.governance_context.mission_id,
            "governance-context-integration",
        )
        self.assertEqual(
            context.governance_context.resource_scope,
            ("workspace", "desktop"),
        )
        self.assertEqual(
            dict(context.governance_context.authorization_provenance),
            {"source": "explicit_user_authorization"},
        )

    def test_governance_context_remains_immutable(self):
        context = CapabilityContext()

        with self.assertRaises(AttributeError):
            context.governance_context = GovernanceContext(
                principal="Zoey",
            )

    def test_existing_context_behavior_remains_intact(self):
        context = CapabilityContext(
            workspace_root=Path("workspace"),
            dependencies={"truth_gate": "test"},
            permissions={"filesystem.read"},
        )

        self.assertEqual(context.workspace_root, Path("workspace"))
        self.assertEqual(
            context.get_dependency("truth_gate"),
            "test",
        )
        self.assertEqual(
            context.permissions,
            frozenset({"filesystem.read"}),
        )


if __name__ == "__main__":
    unittest.main()
