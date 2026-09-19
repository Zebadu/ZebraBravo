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


def read(path):
    result = development.execute(
        "read",
        {"path": path},
    )

    if not result.ok:
        raise RuntimeError(
            f"Could not read {path}: "
            f"{result.code}: {result.message}"
        )

    return result.data["content"]


def write(path, content):
    result = development.execute(
        "write",
        {
            "path": path,
            "content": content,
        },
    )

    print(
        "GOVERNED WRITE:",
        path,
        result.ok,
        result.code,
        result.message,
    )

    if result.data is not None:
        print(result.data)

    if not result.ok:
        raise SystemExit(1)


CAPABILITIES = '''(
                "archive",
                "continuity",
                "desktop",
                "filesystem",
                "filesystem_write",
                "git",
                "powershell_xray",
                "test",
                "truth",
                "visual",
                "zoey_identity",
            )'''


def repair_runtime_test():
    path = "tests/test_capability_runtime.py"
    content = read(path)

    marker = "    def test_runtime_registers_capabilities(self):"
    start = content.index(marker)

    assertion_start = content.index(
        "        self.assertEqual(",
        start,
    )

    assertion_end = content.index(
        "\n\n    def ",
        assertion_start,
    )

    replacement = '''        self.assertEqual(
            runtime.capability_names(),
            CAPABILITIES,
        )'''

    content = (
        content[:assertion_start]
        + replacement
        + content[assertion_end:]
    )

    write(path, content)


def repair_development_test():
    path = "tests/test_development_interface.py"
    content = read(path)

    marker = (
        "    def test_project_info_reports_workspace_and_capabilities"
        "(self):"
    )
    start = content.index(marker)

    assertion_start = content.index(
        '        self.assertEqual(\n'
        '            result.data["capabilities"],',
        start,
    )

    assertion_end = content.index(
        "\n\n    def ",
        assertion_start,
    )

    replacement = '''        self.assertEqual(
            result.data["capabilities"],
            CAPABILITIES,
        )'''

    content = (
        content[:assertion_start]
        + replacement
        + content[assertion_end:]
    )

    write(path, content)


runtime_test = read("tests/test_capability_runtime.py")

if "CAPABILITIES =" not in runtime_test:
    insert_at = runtime_test.index(
        "class CapabilityRuntimeTests"
    )

    runtime_test = (
        runtime_test[:insert_at]
        + "CAPABILITIES = "
        + CAPABILITIES
        + "\n\n"
        + runtime_test[insert_at:]
    )

    write(
        "tests/test_capability_runtime.py",
        runtime_test,
    )


development_test = read("tests/test_development_interface.py")

if "CAPABILITIES =" not in development_test:
    insert_at = development_test.index(
        "class DevelopmentInterfaceTests"
    )

    development_test = (
        development_test[:insert_at]
        + "CAPABILITIES = "
        + CAPABILITIES
        + "\n\n"
        + development_test[insert_at:]
    )

    write(
        "tests/test_development_interface.py",
        development_test,
    )


repair_runtime_test()
repair_development_test()

print("CAPABILITY ASSERTION REPAIR COMPLETE.")