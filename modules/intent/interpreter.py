from .contracts import Intent


class IntentInterpreter:
    """Convert explicit commands into validated Intent objects."""

    def interpret(self, command):
        command = command.strip()

        if not command:
            raise ValueError("Command cannot be empty")

        parts = command.split(maxsplit=1)
        action = parts[0].lower()

        if action == "read_file":
            if len(parts) != 2 or not parts[1].strip():
                raise ValueError("read_file requires a path")

            return Intent(
                name="read_file",
                capability="filesystem",
                operation="read",
                parameters={
                    "path": parts[1].strip(),
                },
            )

        if action == "list_files":
            path = "."

            if len(parts) == 2 and parts[1].strip():
                path = parts[1].strip()

            return Intent(
                name="list_files",
                capability="filesystem",
                operation="list",
                parameters={
                    "path": path,
                },
            )

        raise ValueError(f"Unknown command: {action}")