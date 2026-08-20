import uuid


class TruthGateService:
    VALID_STATUSES = {
        "HYPOTHESIS",
        "VERIFIED",
        "DISPROVED",
    }

    def __init__(self, repository):
        self.repository = repository

    def get_current(self):
        return self.repository.load()

    def get_claim(self, claim_id):
        ledger = self.repository.load()

        for claim in ledger["claims"]:
            if claim["id"] == claim_id:
                return claim

        raise ValueError(
            f"Unknown claim: {claim_id}"
        )

    def create_claim(self, claim_text):
        if not isinstance(claim_text, str) or not claim_text.strip():
            raise ValueError(
                "Claim cannot be empty."
            )

        ledger = self.repository.load()

        claim = {
            "id": str(uuid.uuid4()),
            "claim": claim_text,
            "status": "HYPOTHESIS",
            "evidence": [],
        }

        ledger["claims"].append(claim)
        self.repository.save(ledger)

        return claim

    def add_evidence(self, claim_id, evidence):
        if not isinstance(evidence, dict) or not evidence:
            raise ValueError(
                "Evidence must contain information."
            )

        ledger = self.repository.load()

        for claim in ledger["claims"]:
            if claim["id"] == claim_id:
                if evidence not in claim["evidence"]:
                    claim["evidence"].append(evidence)

                self.repository.save(ledger)
                return claim

        raise ValueError(
            f"Unknown claim: {claim_id}"
        )

    def set_status(self, claim_id, status):
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid claim status: {status}"
            )

        ledger = self.repository.load()

        for claim in ledger["claims"]:
            if claim["id"] == claim_id:
                if (
                    status in {"VERIFIED", "DISPROVED"}
                    and not claim["evidence"]
                ):
                    raise ValueError(
                        "Verified or disproved claims require evidence."
                    )

                claim["status"] = status
                self.repository.save(ledger)

                return claim

        raise ValueError(
            f"Unknown claim: {claim_id}"
        )