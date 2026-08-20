import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime  # noqa: E402
from json_truth_repository import JsonTruthRepository  # noqa: E402
from truth_gate import TruthGateService  # noqa: E402


class TruthCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.truth_file = (
            Path(self.temp_dir.name)
            / "truth_ledger.json"
        )

        self.truth_file.write_text(
            '{\n    "version": 1,\n    "claims": []\n}',
            encoding="utf-8",
        )

        repository = JsonTruthRepository(
            self.truth_file
        )

        self.truth_service = TruthGateService(
            repository
        )

        self.runtime = CapabilityRuntime(
            workspace_root=Path(self.temp_dir.name),
            permissions={"truth.read"},
            dependencies={
                "truth_gate": self.truth_service,
            },
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_truth_capability_reads_current_ledger(self):
        result = self.runtime.execute(
            "truth",
            {
                "operation": "get_current",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data,
            {
                "version": 1,
                "claims": [],
            },
        )

    def test_truth_capability_reads_existing_claim(self):
        claim = self.truth_service.create_claim(
            "ZebraBravo is a very well-behaved, highly disciplined, increasingly capable ZebraBravo."
        )

        result = self.runtime.execute(
            "truth",
            {
                "operation": "get_claim",
                "claim_id": claim["id"],
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.data["id"],
            claim["id"],
        )
        self.assertEqual(
            result.data["claim"],
            claim["claim"],
        )
        self.assertEqual(
            result.data["status"],
            "HYPOTHESIS",
        )


if __name__ == "__main__":
    unittest.main()