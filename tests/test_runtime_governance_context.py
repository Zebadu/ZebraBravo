import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

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


if __name__ == "__main__":
    unittest.main()
