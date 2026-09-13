from memory_manager import MemoryManager


class Assistant:
    def __init__(self, project_root):
        self.memory_manager = MemoryManager(project_root)

    def process_command(self, command):
        command = command.strip()

        if not command:
            return True

        if command.lower() == "exit":
            print("Goodbye, Zeb.")
            return False

        if command.lower() == "help":
            self.show_help()
            return True

        if command.lower().startswith("remember "):
            self.remember_command(command[9:].strip())
            return True

        if command.lower().startswith("search "):
            self.search_command(command[7:].strip())
            return True

        if command.lower().startswith("show "):
            self.show_command(command[5:].strip())
            return True

        if command.lower().startswith("delete "):
            self.delete_command(command[7:].strip())
            return True

        print("Unknown command. Type 'help' for available commands.")
        return True

    def remember_command(self, text):
        parts = text.split(" ", 1)

        if len(parts) == 1:
            print("Please provide memory type and content.")
            print("Example: remember fact Zeb likes motorcycles.")
            return

        memory_type = parts[0].lower()
        content = parts[1].strip()

        try:
            self.memory_manager.add_memory(content, memory_type)
            print("Memory saved.")

        except ValueError as error:
            print(error)

    def search_command(self, search_text):
        if not search_text:
            print("Please provide something to search for.")
            return

        results = self.memory_manager.search(search_text)

        if results:
            print(f"Found {len(results)} memory(s).")

            for memory in results:
                print(
                    f"[{memory['id']}] "
                    f"{memory['content']}"
                )
        else:
            print("No memories found.")

    def show_command(self, memory_id_text):
        try:
            memory_id = int(memory_id_text)

        except ValueError:
            print("Please provide a valid memory ID.")
            return

        memory = self.memory_manager.get_by_id(memory_id)

        if memory:
            print(f"ID: {memory['id']}")
            print(f"Type: {memory['type']}")
            print(f"Created: {memory['created']}")
            print(f"Content: {memory['content']}")

        else:
            print("Memory not found.")

    def delete_command(self, memory_id_text):
        try:
            memory_id = int(memory_id_text)

        except ValueError:
            print("Please provide a valid memory ID.")
            return

        if self.memory_manager.delete_memory(memory_id):
            print("Memory deleted.")
        else:
            print("Memory not found.")

    def show_help(self):
        print()
        print("Available commands:")
        print("  remember <type> <text> - Save a new memory")
        print("  search <text>         - Search memories")
        print("  show <id>             - Show a specific memory")
        print("  delete <id>           - Delete a memory")
        print("  help                  - Show this help")
        print("  exit                  - Exit ZebraBravo")
        print()
        print("Memory types:")
        print("  fact")
        print("  preference")
        print("  person")
        print("  project")
        print("  event")
        print("  instruction")
        print()
