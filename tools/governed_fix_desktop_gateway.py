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

if "from capabilities.contracts import CapabilityResult" not in content:
    content = content.replace(
        "from pywinauto import Desktop",
        "from capabilities.contracts import CapabilityResult\n"
        "from collections.abc import Mapping\n\n"
        "from pywinauto import Desktop",
        1,
    )

if "    def execute(self, request):" not in content:
    marker = "    def inspect(self):"

    method = """    def execute(self, request):
        if not isinstance(request, Mapping):
            return CapabilityResult(
                ok=False,
                message="Desktop request must be a mapping.",
                code="invalid_request",
            )

        operation = request.get("operation")

        if operation == "inspect":
            return CapabilityResult(
                ok=True,
                data=self.inspect(),
            )

        return CapabilityResult(
            ok=False,
            message=f"Unsupported desktop operation: {operation}",
            code="unsupported_operation",
        )

"""

    if content.count(marker) != 1:
        raise RuntimeError(
            "Expected exactly one inspect method."
        )

    content = content.replace(
        marker,
        method + marker,
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