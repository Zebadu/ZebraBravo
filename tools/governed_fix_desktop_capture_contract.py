import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"

sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime


runtime = CapabilityRuntime(
    workspace_root=PROJECT_ROOT,
    permissions={
        "filesystem.read",
        "filesystem.write",
        "git.read",
    },
)

runtime.development_service.set_development_mode(True)

development = runtime.development_service.development_interface

read_result = development.execute(
    "read",
    {
        "path": "ui/desktop/gateway.py",
    },
)

if not read_result.ok:
    raise RuntimeError(
        f"Could not read gateway.py: "
        f"{read_result.code}: {read_result.message}"
    )

content = read_result.data["content"]

old_block = """        if operation == "capture":
            return CapabilityResult(
                ok=True,
                data=self.capture(request.get("title")),
            )

"""

new_block = """        if operation == "capture":
            return self.capture(request.get("title"))

"""

if old_block not in content:
    raise RuntimeError(
        "Expected desktop capture dispatch block was not found."
    )

content = content.replace(
    old_block,
    new_block,
    1,
)

write_result = development.execute(
    "write",
    {
        "path": "ui/desktop/gateway.py",
        "content": content,
    },
)

print(
    "GOVERNED WRITE:",
    write_result.ok,
    write_result.code,
    write_result.message,
)

if write_result.ok:
    print(write_result.data)