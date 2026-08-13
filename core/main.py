import json
from pathlib import Path
from datetime import datetime
import sys

# Locate the ZebraBravo project folder

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow ZebraBravo to access its modules

sys.path.insert(0, str(PROJECT_ROOT / "Modules"))

from memory_manager import MemoryManager
from assistant import Assistant

# Load configuration

CONFIG_FILE = PROJECT_ROOT / "Config" / "config.json"

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = json.load(file)

# Load memory through the MemoryManager

memory_manager = MemoryManager(PROJECT_ROOT)
memory = memory_manager.load()

# Locate the Logs folder

LOGS_FOLDER = PROJECT_ROOT / "Logs"
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
print(f"Memory loaded: {len(memory['memories'])} memories.")
print()
print("Type 'help' for available commands.")
print()

# Start the Assistant command interface

assistant = Assistant(PROJECT_ROOT)

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