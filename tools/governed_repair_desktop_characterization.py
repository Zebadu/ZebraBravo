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
        {
            "path": path,
        },
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


runtime_test = read("tests/test_capability_runtime.py")

old_runtime = '''            "archive",
            "continuity",
            "filesystem",
'''

new_runtime = '''            "archive",
            "continuity",
            "desktop",
            "filesystem",
'''

if old_runtime not in runtime_test:
    raise RuntimeError(
        "Expected capability tuple in test_capability_runtime.py was not found."
    )

runtime_test = runtime_test.replace(
    old_runtime,
    new_runtime,
    1,
)

write(
    "tests/test_capability_runtime.py",
    runtime_test,
)


development_test = read("tests/test_development_interface.py")

old_development = '''            "archive",
            "continuity",
            "filesystem",
'''

new_development = '''            "archive",
            "continuity",
            "desktop",
            "filesystem",
'''

if old_development not in development_test:
    raise RuntimeError(
        "Expected capability tuple in test_development_interface.py was not found."
    )

development_test = development_test.replace(
    old_development,
    new_development,
    1,
)

write(
    "tests/test_development_interface.py",
    development_test,
)


characterization_test = read(
    "tests/test_zebrabravo_010_characterization.py"
)

old_characterization = '''            "modules/capabilities/runtime.py",
            "modules/capabilities/development.py",
'''

new_characterization = '''            "modules/capabilities/runtime.py",
            "modules/capabilities/development.py",
            "modules/capabilities/plugins/desktop.py",
'''

if old_characterization not in characterization_test:
    raise RuntimeError(
        "Expected startup source list in characterization test was not found."
    )

characterization_test = characterization_test.replace(
    old_characterization,
    new_characterization,
    1,
)

write(
    "tests/test_zebrabravo_010_characterization.py",
    characterization_test,
)