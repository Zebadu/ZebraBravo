import json


class JsonMemoryRepository:
    VALID_MEMORY_TYPES = {
        "fact",
        "preference",
        "person",
        "project",
        "event",
        "instruction"
    }

    def __init__(self, memory_file):
        self.memory_file = memory_file

    def load(self):
        with open(self.memory_file, "r", encoding="utf-8") as file:
            memory = json.load(file)

        self.validate_memory(memory)

        return memory

    def save(self, memory):
        self.validate_memory(memory)

        with open(self.memory_file, "w", encoding="utf-8") as file:
            json.dump(memory, file, indent=4)

    def validate_memory(self, memory):
        if not isinstance(memory, dict):
            raise ValueError("Memory file must contain a JSON object.")

        if "memories" not in memory:
            raise ValueError("Memory file is missing the 'memories' field.")

        if not isinstance(memory["memories"], list):
            raise ValueError("'memories' must be a list.")

        if "next_id" not in memory:
            raise ValueError("Memory file is missing the 'next_id' field.")

        if not isinstance(memory["next_id"], int):
            raise ValueError("'next_id' must be an integer.")

        for item in memory["memories"]:
            if not isinstance(item, dict):
                raise ValueError("Each memory must be a JSON object.")

            required_fields = {
                "id",
                "type",
                "created",
                "content"
            }

            missing_fields = required_fields - item.keys()

            if missing_fields:
                raise ValueError(
                    f"Memory is missing fields: "
                    f"{', '.join(sorted(missing_fields))}"
                )

            if not isinstance(item["id"], int):
                raise ValueError("Memory ID must be an integer.")

            if item["type"] not in self.VALID_MEMORY_TYPES:
                raise ValueError(
                    f"Invalid memory type: {item['type']}"
                )

            if not isinstance(item["content"], str):
                raise ValueError("Memory content must be text.")
