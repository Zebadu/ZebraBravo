import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.governance import GovernanceContext  # noqa: E402


class GovernanceContextTests(unittest.TestCase):
    def test_defaults_are_safe_and_empty(self):
        context = GovernanceContext()

        self.assertEqual(context.principal, "")
        self.assertEqual(context.authority, "")
        self.assertEqual(context.mission_id, "")
        self.assertEqual(context.resource_scope, ())
        self.assertEqual(dict(context.authorization_provenance), {})

    def test_context_preserves_governance_fields(self):
        context = GovernanceContext(
            principal="Zeb",
            authority="owner",
            mission_id="mission-001",
            resource_scope=("onedrive", "desktop"),
            authorization_provenance={
                "source": "explicit_user_authorization",
                "session": "test",
            },
        )

        self.assertEqual(context.principal, "Zeb")
        self.assertEqual(context.authority, "owner")
        self.assertEqual(context.mission_id, "mission-001")
        self.assertEqual(context.resource_scope, ("onedrive", "desktop"))
        self.assertEqual(
            dict(context.authorization_provenance),
            {
                "source": "explicit_user_authorization",
                "session": "test",
            },
        )

    def test_context_is_immutable(self):
        context = GovernanceContext(principal="Zeb")

        with self.assertRaises(AttributeError):
            context.principal = "Zoey"

    def test_provenance_mapping_is_immutable(self):
        context = GovernanceContext(
            authorization_provenance={"source": "test"},
        )

        with self.assertRaises(TypeError):
            context.authorization_provenance["source"] = "changed"

    def test_resource_scope_is_normalized_to_tuple(self):
        context = GovernanceContext(
            resource_scope=["onedrive", "desktop"],
        )

        self.assertEqual(context.resource_scope, ("onedrive", "desktop"))


if __name__ == "__main__":
    unittest.main()
