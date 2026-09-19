from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime


path = PROJECT_ROOT / "modules" / "capabilities" / "visual_observation.py"

source = path.read_text(encoding="utf-8-sig")

old_width = '        width=capture["size"][0],'
old_height = '        height=capture["size"][1],'

new_width = '        width=capture["width"],'
new_height = '        height=capture["height"],'

if old_width not in source or old_height not in source:
    raise RuntimeError("Expected VisualObservation capture contract was not found.")

updated = source.replace(old_width, new_width, 1)
updated = updated.replace(old_height, new_height, 1)

runtime = CapabilityRuntime(
    workspace_root=PROJECT_ROOT,
    permissions={"filesystem.write"},
)

runtime.development_service.set_development_mode(True)

result = runtime.development_service.development_interface.execute(
    "write",
    {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "content": updated,
    },
)

print("GOVERNED WRITE:", result.ok, result.code)
print(result.message)