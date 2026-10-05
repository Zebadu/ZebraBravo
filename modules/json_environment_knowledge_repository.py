import json


class JsonEnvironmentKnowledgeRepository:
    VALID_STATUSES = {
        "unknown",
        "discovered",
        "verified",
        "failed",
        "stale",
    }

    def __init__(self, knowledge_file):
        self.knowledge_file = knowledge_file

    def load(self):
        with open(self.knowledge_file, "r", encoding="utf-8") as file:
            knowledge = json.load(file)

        self.validate_knowledge(knowledge)

        return knowledge

    def save(self, knowledge):
        self.validate_knowledge(knowledge)

        with open(self.knowledge_file, "w", encoding="utf-8") as file:
            json.dump(knowledge, file, indent=4)

    def validate_knowledge(self, knowledge):
        if not isinstance(knowledge, dict):
            raise ValueError(
                "Environment knowledge file must contain a JSON object."
            )

        if "knowledge_version" not in knowledge:
            raise ValueError(
                "Environment knowledge is missing 'knowledge_version'."
            )

        if not isinstance(knowledge["knowledge_version"], int):
            raise ValueError(
                "Environment knowledge version must be an integer."
            )

        if "entries" not in knowledge:
            raise ValueError(
                "Environment knowledge is missing the 'entries' field."
            )

        if not isinstance(knowledge["entries"], list):
            raise ValueError(
                "'entries' must be a list."
            )

        for entry in knowledge["entries"]:
            if not isinstance(entry, dict):
                raise ValueError(
                    "Each environment knowledge entry must be a JSON object."
                )

            required_fields = {
                "id",
                "kind",
                "name",
                "location",
                "status",
                "version",
                "verified_at",
                "source",
                "evidence",
                "metadata",
            }

            missing_fields = required_fields - entry.keys()

            if missing_fields:
                raise ValueError(
                    "Environment knowledge entry is missing fields: "
                    f"{', '.join(sorted(missing_fields))}"
                )

            if not isinstance(entry["id"], str):
                raise ValueError("Environment knowledge ID must be text.")

            if not isinstance(entry["kind"], str):
                raise ValueError("Environment knowledge kind must be text.")

            if not isinstance(entry["name"], str):
                raise ValueError("Environment knowledge name must be text.")

            if not isinstance(entry["location"], str):
                raise ValueError(
                    "Environment knowledge location must be text."
                )

            if entry["status"] not in self.VALID_STATUSES:
                raise ValueError(
                    f"Invalid environment knowledge status: "
                    f"{entry['status']}"
                )

            if not isinstance(entry["version"], str):
                raise ValueError(
                    "Environment knowledge version must be text."
                )

            if not isinstance(entry["verified_at"], str):
                raise ValueError(
                    "Environment knowledge verified_at must be text."
                )

            if not isinstance(entry["source"], str):
                raise ValueError(
                    "Environment knowledge source must be text."
                )

            if not isinstance(entry["evidence"], list):
                raise ValueError(
                    "Environment knowledge evidence must be a list."
                )

            if not isinstance(entry["metadata"], dict):
                raise ValueError(
                    "Environment knowledge metadata must be an object."
                )
