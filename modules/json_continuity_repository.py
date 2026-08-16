import json


class JsonContinuityRepository:
    def __init__(self, continuity_file):
        self.continuity_file = continuity_file

    def load(self):
        with open(self.continuity_file, "r", encoding="utf-8") as file:
            continuity = json.load(file)

        self.validate_continuity(continuity)

        return continuity

    def save(self, continuity):
        self.validate_continuity(continuity)

        with open(self.continuity_file, "w", encoding="utf-8") as file:
            json.dump(continuity, file, indent=4)

    def validate_continuity(self, continuity):
        if not isinstance(continuity, dict):
            raise ValueError(
                "Continuity file must contain a JSON object."
            )

        required_fields = {
            "project",
            "continuity_version",
            "checkpoint",
            "completed",
            "decisions",
            "rejected",
            "open_questions",
            "next_action",
            "architecture_notes",
            "important_context",
        }

        missing_fields = required_fields - continuity.keys()

        if missing_fields:
            raise ValueError(
                "Continuity is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )

        if continuity["project"] != "ZebraBravo":
            raise ValueError(
                "Continuity project must be ZebraBravo."
            )

        if not isinstance(continuity["continuity_version"], int):
            raise ValueError(
                "Continuity version must be an integer."
            )

        if not isinstance(continuity["checkpoint"], dict):
            raise ValueError(
                "Continuity checkpoint must be an object."
            )

        list_fields = {
            "completed",
            "decisions",
            "rejected",
            "open_questions",
            "architecture_notes",
            "important_context",
        }

        for field in list_fields:
            if not isinstance(continuity[field], list):
                raise ValueError(
                    f"Continuity field '{field}' must be a list."
                )

        if not isinstance(continuity["next_action"], str):
            raise ValueError(
                "Continuity next_action must be text."
            )