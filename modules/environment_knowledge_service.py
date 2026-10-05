class EnvironmentKnowledgeService:
    def __init__(self, repository):
        self.repository = repository

    def get_all(self):
        return self.repository.load()

    def get_by_id(self, entry_id):
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError(
                "Environment knowledge ID must be text."
            )

        knowledge = self.repository.load()

        for entry in knowledge["entries"]:
            if entry["id"] == entry_id:
                return entry

        return None

    def search(self, search_text):
        if not isinstance(search_text, str):
            raise ValueError(
                "Environment knowledge search text must be text."
            )

        search_text = search_text.lower()
        knowledge = self.repository.load()

        return [
            entry
            for entry in knowledge["entries"]
            if (
                search_text in entry["id"].lower()
                or search_text in entry["kind"].lower()
                or search_text in entry["name"].lower()
                or search_text in entry["location"].lower()
                or search_text in entry["status"].lower()
            )
        ]

    def record(self, entry):
        if not isinstance(entry, dict):
            raise ValueError(
                "Environment knowledge entry must be an object."
            )

        knowledge = self.repository.load()

        if any(
            existing["id"] == entry.get("id")
            for existing in knowledge["entries"]
        ):
            raise ValueError(
                f"Environment knowledge ID already exists: "
                f"{entry.get('id')}"
            )

        knowledge["entries"].append(entry)
        self.repository.save(knowledge)

    def update(self, entry_id, updates):
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError(
                "Environment knowledge ID must be text."
            )

        if not isinstance(updates, dict):
            raise ValueError(
                "Environment knowledge updates must be an object."
            )

        if updates.get("status") == "verified":
            raise ValueError(
                "Use verify() to promote environment knowledge to verified."
            )

        knowledge = self.repository.load()

        for entry in knowledge["entries"]:
            if entry["id"] == entry_id:
                entry.update(updates)
                self.repository.save(knowledge)
                return True

        return False

    def verify(self, entry_id, evidence, source):
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError(
                "Environment knowledge ID must be text."
            )

        if not isinstance(evidence, list) or not evidence:
            raise ValueError(
                "Verification evidence must be a non-empty list."
            )

        if not all(isinstance(item, str) and item for item in evidence):
            raise ValueError(
                "Verification evidence must contain non-empty text."
            )

        if not isinstance(source, str) or not source:
            raise ValueError(
                "Verification source must be text."
            )

        knowledge = self.repository.load()

        for entry in knowledge["entries"]:
            if entry["id"] == entry_id:
                entry["status"] = "verified"
                entry["verified_at"] = __import__("datetime").datetime.now().astimezone().isoformat()
                entry["source"] = source
                entry["evidence"].extend(evidence)
                self.repository.save(knowledge)
                return True

        return False
