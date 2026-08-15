from memory_manager import MemoryManager


class Assistant:
    def __init__(
        self,
        project_root,
        memory_service=None,
        capability_runtime=None,
    ):
        if memory_service is None:
            memory_service = MemoryManager(project_root)

        self.memory_manager = memory_service
        self.capability_runtime = capability_runtime

    def process_command(self, command):
        command = command.strip()

        if not command:
            return

        if command.lower() == "exit":
            print("Goodbye, Zeb.")
            return False

        if command.lower() == "help":
            self.show_help()
            return True

        if command.lower().startswith("remember "):
            content = command[9:].strip()

            if content:
                self.memory_manager.add_memory(content)
                print("Memory saved.")
            else:
                print("Please provide something to remember.")

            return True

        if command.lower().startswith("search "):
            search_text = command[7:].strip()

            if search_text:
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
            else:
                print("Please provide something to search for.")

            return True

        if command.lower().startswith("show "):
            try:
                memory_id = int(command[5:].strip())
                memory = self.memory_manager.get_by_id(memory_id)

                if memory:
                    print(f"ID: {memory['id']}")
                    print(f"Type: {memory['type']}")
                    print(f"Created: {memory['created']}")
                    print(f"Content: {memory['content']}")
                else:
                    print("Memory not found.")

            except ValueError:
                print("Please provide a valid memory ID.")

            return True

        if command.lower().startswith("delete "):
            try:
                memory_id = int(command[7:].strip())

                if self.memory_manager.delete_memory(memory_id):
                    print("Memory deleted.")
                else:
                    print("Memory not found.")

            except ValueError:
                print("Please provide a valid memory ID.")

            return True

        print("Unknown command. Type 'help' for available commands.")
        return True

    def execute_capability(self, capability_name, request):
        if self.capability_runtime is None:
            raise RuntimeError("Capability runtime is not configured")

        return self.capability_runtime.execute(
            capability_name,
            request,
        )

    def show_help(self):
        print()
        print("Available commands:")
        print("  remember <text>  - Save a new memory")
        print("  search <text>    - Search memories")
        print("  show <id>        - Show a specific memory")
        print("  delete <id>      - Delete a memory")
        print("  help             - Show this help")
        print("  exit             - Exit ZebraBravo")
        print()