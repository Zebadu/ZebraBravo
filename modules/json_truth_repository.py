import json


class JsonTruthRepository:
    def __init__(self, truth_file):
        self.truth_file = truth_file

    def load(self):
        with open(self.truth_file, "r", encoding="utf-8") as file:
            truth = json.load(file)

        self.validate_truth(truth)

        return truth

    def save(self, truth):
        self.validate_truth(truth)

        with open(self.truth_file, "w", encoding="utf-8") as file:
            json.dump(truth, file, indent=4)

    def validate_truth(self, truth):
        if not isinstance(truth, dict):
            raise ValueError(
                "Truth file must contain a JSON object."
            )

        required_fields = {
            "claims",
        }

        missing_fields = required_fields - truth.keys()

        if missing_fields:
            raise ValueError(
                "Truth is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )

        if not isinstance(truth["claims"], list):
            raise ValueError(
                "Truth field 'claims' must be a list."
            )