from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime


desktop_path = PROJECT_ROOT / "modules" / "capabilities" / "plugins" / "desktop.py"

source = desktop_path.read_text(encoding="utf-8-sig")

import_line = "from capabilities.visual_observation import VisualObservation\n"

if import_line not in source:
    source = source.replace(
        "from capabilities.contracts import CapabilityMetadata, CapabilityResult\n",
        "from capabilities.contracts import CapabilityMetadata, CapabilityResult\n"
        + import_line,
        1,
    )

old = "        return desktop_gateway.execute(request)"

new = """        result = desktop_gateway.execute(request)

        if request.get("operation") == "capture" and result.ok:
            return CapabilityResult(
                ok=True,
                data=VisualObservation.from_capture(result.data),
            )

        return result"""

if old not in source:
    raise RuntimeError("Expected DesktopCapability delegation was not found.")

if "VisualObservation.from_capture(result.data)" not in source:
    source = source.replace(old, new, 1)

runtime = CapabilityRuntime(
    workspace_root=PROJECT_ROOT,
    permissions={"filesystem.write"},
)

runtime.development_service.set_development_mode(True)

result = runtime.development_service.development_interface.execute(
    "write",
    {
        "path": str(desktop_path.relative_to(PROJECT_ROOT)),
        "content": source,
    },
)

print("GOVERNED WRITE:", result.ok, result.code)
print(result.message)