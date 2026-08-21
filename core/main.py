import json
from pathlib import Path
from datetime import datetime
import sys


# Locate the ZebraBravo project folder

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow ZebraBravo to access its modules

sys.path.insert(0, str(PROJECT_ROOT / "modules"))

from assistant import Assistant
from capabilities.runtime import CapabilityRuntime
from json_memory_repository import JsonMemoryRepository
from memory_service import MemoryService


# Load configuration

CONFIG_FILE = PROJECT_ROOT / "config" / "config.json"

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = json.load(file)


# Create the memory service

MEMORY_FILE = PROJECT_ROOT / "memory" / "memory.json"
memory_repository = JsonMemoryRepository(MEMORY_FILE)
memory_service = MemoryService(memory_repository)
memory = memory_service.search("")


# Create the controlled capability runtime

capability_runtime = CapabilityRuntime(
    workspace_root=PROJECT_ROOT,
    permissions={"filesystem.read"},
)


# Locate the Logs folder

LOGS_FOLDER = PROJECT_ROOT / "logs"
LOGS_FOLDER.mkdir(exist_ok=True)


# Create a startup log entry

LOG_FILE = LOGS_FOLDER / "zebrabravo.log"

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(LOG_FILE, "a", encoding="utf-8") as file:
    file.write(
        f"{timestamp} - {config['name']} started - "
        f"{config['assistant']} online.\n"
    )


# Start ZebraBravo

print(config["name"])
print(f"{config['assistant']} is online.")
print("System initialization successful.")
print(f"Memory loaded: {len(memory)} memories.")
print()
print("Type 'help' for available commands.")
print()


# Start the Assistant command interface

assistant = Assistant(
    PROJECT_ROOT,
    memory_service,
    capability_runtime=capability_runtime,
)


while True:
    try:
        command = input("> ")

        if not assistant.process_command(command):
            break

    except KeyboardInterrupt:
        print()
        print("ZebraBravo shutting down.")
        break

    except EOFError:
        print()
        print("ZebraBravo shutting down.")
        break