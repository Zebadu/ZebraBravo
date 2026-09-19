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


EXPECTED = '''            (
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
            ),
'''


def repair_capability_tuple(path):
    content = read(path)

    start_marker = "        runtime.capability_names(),"
    if start_marker in content:
        start = content.index(start_marker)
    else:
        start_marker = '        result.data["capabilities"],'
        if start_marker not in content:
            raise RuntimeError(
                f"Could not locate capability assertion in {path}."
            )
        start = content.index(start_marker)

    tuple_start = content.index("(", start)
    tuple_end = content.index(
        "            ),",
        tuple_start,
    ) + len("            ),")

    content = (
        content[:tuple_start]
        + EXPECTED.rstrip("\n")
        + content[tuple_end:]
    )

    write(path, content)


repair_capability_tuple(
    "tests/test_capability_runtime.py"
)

repair_capability_tuple(
    "tests/test_development_interface.py"
)


characterization_path = (
    "tests/test_zebrabravo_010_characterization.py"
)

content = read(characterization_path)

desktop_entry = (
    '            "modules/capabilities/plugins/desktop.py",\n'
)

test_entry = (
    '            "modules/capabilities/plugins/test.py",\n'
)

if desktop_entry not in content:
    marker = test_entry

    if marker not in content:
        raise RuntimeError(
            "Could not locate test.py source entry in "
            "the characterization test."
        )

    content = content.replace(
        marker,
        desktop_entry + marker,
        1,
    )

write(characterization_path, content)

print("DESKTOP TEST CHARACTERIZATION REPAIR COMPLETE.")