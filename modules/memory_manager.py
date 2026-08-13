import json
from pathlib import Path
from datetime import datetime


class MemoryManager:
    VALID_MEMORY_TYPES = {
        "fact",
        "preference",
        "person",
        "project",
        "event",
        "instruction"
    }

    def __init__(self, project_root):
        self.memory_file = Path(project_root) / "Memory" / "memory.json"

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

    def add_memory(self, memory_text, memory_type="fact"):
        if memory_type not in self.VALID_MEMORY_TYPES:
            raise ValueError(
                f"Invalid memory type: {memory_type}. "
                f"Valid types: {', '.join(sorted(self.VALID_MEMORY_TYPES))}"
            )

        memory = self.load()

        new_memory = {
            "id": memory["next_id"],
            "type": memory_type,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": memory_text
        }

        memory["memories"].append(new_memory)
        memory["next_id"] += 1

        self.save(memory)

    def search(self, search_text):
        memory = self.load()
        results = []

        search_text = search_text.lower()

        for item in memory["memories"]:
            if search_text in item["content"].lower():
                results.append(item)

        return results

    def get_by_id(self, memory_id):
        memory = self.load()

        for item in memory["memories"]:
            if item["id"] == memory_id:
                return item

        return None

    def update_memory(self, memory_id, new_content):
        memory = self.load()

        for item in memory["memories"]:
            if item["id"] == memory_id:
                item["content"] = new_content
                self.save(memory)
                return True

        return False

    def delete_memory(self, memory_id):
        memory = self.load()

        for index, item in enumerate(memory["memories"]):
            if item["id"] == memory_id:
                del memory["memories"][index]
                self.save(memory)
                return True

        return False