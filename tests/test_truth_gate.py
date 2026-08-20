import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from json_truth_repository import JsonTruthRepository  # noqa: E402
from truth_gate import TruthGateService  # noqa: E402


class TruthGateTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.truth_file = Path(self.temp_dir.name) / "truth_ledger.json"

        self.initial_record = {
            "version": 1,
            "claims": [],
        }

        self.truth_file.write_text(
            __import__("json").dumps(
                self.initial_record,
                indent=4,
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_service(self):
        repository = JsonTruthRepository(self.truth_file)
        return TruthGateService(repository)

    def test_empty_ledger_loads(self):
        service = self.create_service()

        ledger = service.get_current()

        self.assertEqual(ledger["version"], 1)
        self.assertEqual(ledger["claims"], [])

    def test_create_claim(self):
        service = self.create_service()

        claim = service.create_claim(
            "ZebraBravo has a verified test baseline."
        )

        self.assertEqual(
            claim["claim"],
            "ZebraBravo has a verified test baseline.",
        )
        self.assertEqual(
            claim["status"],
            "HYPOTHESIS",
        )
        self.assertEqual(claim["evidence"], [])

    def test_empty_claim_is_rejected(self):
        service = self.create_service()

        with self.assertRaises(ValueError):
            service.create_claim("")

    def test_invalid_status_is_rejected(self):
        service = self.create_service()

        claim = service.create_claim(
            "A claim with an invalid status."
        )

        with self.assertRaises(ValueError):
            service.set_status(
                claim["id"],
                "UNKNOWN",
            )

    def test_verified_claim_requires_evidence(self):
        service = self.create_service()

        claim = service.create_claim(
            "This claim cannot yet be verified."
        )

        with self.assertRaises(ValueError):
            service.set_status(
                claim["id"],
                "VERIFIED",
            )

    def test_evidence_allows_verified_status(self):
        service = self.create_service()

        claim = service.create_claim(
            "ZebraBravo passed its complete test suite."
        )

        service.add_evidence(
            claim["id"],
            {
                "type": "test",
                "description": "76 tests passed.",
            },
        )

        service.set_status(
            claim["id"],
            "VERIFIED",
        )

        current = service.get_claim(claim["id"])

        self.assertEqual(
            current["status"],
            "VERIFIED",
        )
        self.assertEqual(
            len(current["evidence"]),
            1,
        )

    def test_disproved_claim_requires_evidence(self):
        service = self.create_service()

        claim = service.create_claim(
            "This claim is not yet disproved."
        )

        with self.assertRaises(ValueError):
            service.set_status(
                claim["id"],
                "DISPROVED",
            )

    def test_unknown_claim_is_rejected(self):
        service = self.create_service()

        with self.assertRaises(ValueError):
            service.get_claim("missing-claim")

    def test_duplicate_evidence_is_not_added_twice(self):
        service = self.create_service()

        claim = service.create_claim(
            "Evidence should not be duplicated."
        )

        evidence = {
            "type": "test",
            "description": "76 tests passed.",
        }

        service.add_evidence(
            claim["id"],
            evidence,
        )
        service.add_evidence(
            claim["id"],
            evidence,
        )

        current = service.get_claim(claim["id"])

        self.assertEqual(
            len(current["evidence"]),
            1,
        )

    def test_empty_evidence_is_rejected(self):
        service = self.create_service()

        claim = service.create_claim(
            "Evidence must contain information."
        )

        with self.assertRaises(ValueError):
            service.add_evidence(
                claim["id"],
                {},
            )


if __name__ == "__main__":
    unittest.main()