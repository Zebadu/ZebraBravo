import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime
from json_continuity_repository import JsonContinuityRepository
from continuity_service import ContinuityService


class ContinuityCapabilityTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.continuity_file = (
            Path(self.temp_dir.name)
            / "project_continuity.json"
        )

        self.continuity_file.write_text(
            """{
    "project": "ZebraBravo",
    "continuity_version": 3,
    "checkpoint": {
        "date": "2026-09-03",
        "summary": "Continuity capability test.",
        "verified_tests": {
            "passed": 0,
            "subtests_passed": 0,
            "failures": 0
        }
    },
    "zoey": {
        "status": "foundational_project_entity",
        "personality": {
            "traits": [],
            "principles": []
        },
        "future_domains": []
    },
    "completed": [],
    "decisions": [],
    "rejected": [],
    "open_questions": [],
    "next_action": "Test Continuity capability.",
    "architecture_notes": [],
    "important_context": []
}""",
            encoding="utf-8",
        )

        repository = JsonContinuityRepository(
            self.continuity_file
        )

        self.continuity_service = ContinuityService(
            repository
        )

        self.runtime = CapabilityRuntime(
            workspace_root=Path(self.temp_dir.name),
            permissions={"continuity.read"},
            dependencies={
                "continuity": self.continuity_service,
            },
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_continuity_capability_reads_current_record(self):
        result = self.runtime.execute(
            "continuity",
            {
                "operation": "get_current",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["project"],
            "ZebraBravo",
        )
        self.assertEqual(
            result.data["continuity_version"],
            3,
        )

    def test_continuity_capability_reads_next_action(self):
        result = self.runtime.execute(
            "continuity",
            {
                "operation": "get_current",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["next_action"],
            "Test Continuity capability.",
        )

    def test_continuity_capability_requires_dependency(self):
        runtime = CapabilityRuntime(
            workspace_root=Path(self.temp_dir.name),
            permissions={"continuity.read"},
        )

        result = runtime.execute(
            "continuity",
            {
                "operation": "get_current",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(
            result.code,
            "context_required",
        )

    def test_continuity_capability_requires_permission(self):
        runtime = CapabilityRuntime(
            workspace_root=Path(self.temp_dir.name),
            dependencies={
                "continuity": self.continuity_service,
            },
        )

        result = runtime.execute(
            "continuity",
            {
                "operation": "get_current",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(
            result.code,
            "permission_denied",
        )


if __name__ == "__main__":
    unittest.main()