import json
import os
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

# Start the optional local Development Bridge

development_bridge = capability_runtime.development_bridge
development_bridge_config = config.get("development_bridge", {})
development_bridge_started = False

if development_bridge_config.get("enabled", False):
    host = development_bridge_config.get("host", "127.0.0.1")
    port = development_bridge_config.get("port", 0)
    auth_token_env = development_bridge_config.get(
        "auth_token_env",
        "ZEBRABRAVO_DEVELOPMENT_TOKEN",
    )
    auth_token = os.environ.get(auth_token_env)

    if not auth_token:
        raise RuntimeError(
            "Development bridge is enabled, but its authentication "
            f"environment variable '{auth_token_env}' is not set."
        )

    development_bridge.host = host
    development_bridge.port = port
    development_bridge.auth_token = auth_token
    development_bridge.start_background()
    development_bridge_started = True

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

try:
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
finally:
    if development_bridge_started:
        development_bridge.stop()
