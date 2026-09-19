import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "modules"))

from capabilities.runtime import CapabilityRuntime


FILES = {
    "data/zwmd_development_proof.txt": lambda text: "ZebraBravo governed development proof.\nRequest: zwmd-write-002\n",
    "modules/capabilities/policy.py": lambda text: text.rstrip() + "\n",
    "tests/test_desktop_runtime_integration.py": lambda text: text.rstrip() + "\n",
}


runtime = CapabilityRuntime(
    workspace_root=Path.cwd(),
    permissions={"filesystem.read", "filesystem.write"},
)

runtime.development_service.set_development_mode(True)

for path_text, cleaner in FILES.items():
    read_result = runtime.development_service.development_interface.execute(
        "read",
        {"path": path_text},
    )

    if not read_result.ok:
        raise RuntimeError(f"Read failed: {path_text}: {read_result.code}")

    cleaned = cleaner(read_result.data["content"])

    write_result = runtime.development_service.development_interface.execute(
        "write",
        {
            "path": path_text,
            "content": cleaned,
        },
    )

    print(
        "GOVERNED CLEAN:",
        path_text,
        write_result.ok,
        write_result.code,
    )

    if not write_result.ok:
        raise RuntimeError(
            f"Write failed: {path_text}: {write_result.code}"
        )

print("EOF CLEANUP COMPLETE.")
