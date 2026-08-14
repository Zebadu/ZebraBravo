from pathlib import Path

from json_memory_repository import JsonMemoryRepository
from memory_service import MemoryService


class MemoryManager:
    VALID_MEMORY_TYPES = MemoryService.VALID_MEMORY_TYPES

    def __init__(self, project_root):
        self.memory_file = Path(project_root) / "Memory" / "memory.json"
        self.repository = JsonMemoryRepository(self.memory_file)
        self.memory_service = MemoryService(self.repository)

    def load(self):
        return self.repository.load()

    def save(self, memory):
        return self.repository.save(memory)

    def validate_memory(self, memory):
        return self.repository.validate_memory(memory)

    def add_memory(self, memory_text, memory_type="fact"):
        return self.memory_service.add_memory(memory_text, memory_type)

    def search(self, search_text):
        return self.memory_service.search(search_text)

    def get_by_id(self, memory_id):
        return self.memory_service.get_by_id(memory_id)

    def update_memory(self, memory_id, new_content):
        return self.memory_service.update_memory(memory_id, new_content)

    def delete_memory(self, memory_id):
        return self.memory_service.delete_memory(memory_id)
