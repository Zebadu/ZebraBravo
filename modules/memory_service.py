from datetime import datetime


class MemoryService:
    VALID_MEMORY_TYPES = {
        "fact",
        "preference",
        "person",
        "project",
        "event",
        "instruction"
    }

    def __init__(self, repository):
        self.repository = repository

    def add_memory(self, memory_text, memory_type="fact"):
        if memory_type not in self.VALID_MEMORY_TYPES:
            raise ValueError(
                f"Invalid memory type: {memory_type}. "
                f"Valid types: {', '.join(sorted(self.VALID_MEMORY_TYPES))}"
            )

        memory = self.repository.load()

        new_memory = {
            "id": memory["next_id"],
            "type": memory_type,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": memory_text
        }

        memory["memories"].append(new_memory)
        memory["next_id"] += 1

        self.repository.save(memory)

    def search(self, search_text):
        memory = self.repository.load()
        results = []

        search_text = search_text.lower()

        for item in memory["memories"]:
            if search_text in item["content"].lower():
                results.append(item)

        return results

    def get_by_id(self, memory_id):
        memory = self.repository.load()

        for item in memory["memories"]:
            if item["id"] == memory_id:
                return item

        return None

    def update_memory(self, memory_id, new_content):
        memory = self.repository.load()

        for item in memory["memories"]:
            if item["id"] == memory_id:
                item["content"] = new_content
                self.repository.save(memory)
                return True

        return False

    def delete_memory(self, memory_id):
        memory = self.repository.load()

        for index, item in enumerate(memory["memories"]):
            if item["id"] == memory_id:
                del memory["memories"][index]
                self.repository.save(memory)
                return True

        return False
