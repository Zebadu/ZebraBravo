from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime


desktop_path = PROJECT_ROOT / "modules" / "capabilities" / "plugins" / "desktop.py"

source = desktop_path.read_text(encoding="utf-8-sig")

if "from capabilities.visual_observation import VisualObservation" not in source:
    source = (
        "from capabilities.contracts import CapabilityMetadata, CapabilityResult\n"
        "from capabilities.visual_observation import VisualObservation\n"
        + source.split(
            "from capabilities.contracts import CapabilityMetadata, CapabilityResult",
            1,
        )[1]
    )

old = """    result = desktop_gateway.execute(request)

    if request.get("operation") == "capture" and result.ok:
        return CapabilityResult(
            ok=True,
            data=VisualObservation.from_capture(result.data),
        )

    return result
"""

if old in source:
    print("DesktopCapability already contains observation integration.")
    raise SystemExit(0)

old = """    return desktop_gateway.execute(request)
"""

new = """    result = desktop_gateway.execute(request)

    if request.get("operation") == "capture" and result.ok:
        return CapabilityResult(
            ok=True,
            data=VisualObservation.from_capture(result.data),
        )

    return result
"""

if old not in source:
    raise RuntimeError("Expected DesktopCapability delegation was not found.")

updated = source.replace(old, new, 1)

runtime = CapabilityRuntime(
    workspace_root=PROJECT_ROOT,
    permissions={"filesystem.write"},
)

runtime.development_service.set_development_mode(True)

request = {
    "path": str(desktop_path.relative_to(PROJECT_ROOT)),
    "content": updated,
}

result = runtime.development_service.development_interface.execute(
    "write",
    request,
)

print("GOVERNED WRITE:", result.ok, result.code)
print(result.message)