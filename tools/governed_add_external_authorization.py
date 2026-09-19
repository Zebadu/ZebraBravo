import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"

sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime


AUTHORIZATION_FILE = """from hashlib import sha256
from threading import Lock


class ExternalAuthorization:
    \"\"\"One-shot authorization for a specific external capability request.\"\"\"

    def __init__(self):
        self._authorized = set()
        self._lock = Lock()

    @staticmethod
    def _key(capability_name, request):
        normalized = repr(
            (
                capability_name,
                tuple(sorted(request.items())),
            )
        )
        return sha256(normalized.encode("utf-8")).hexdigest()

    def authorize(self, capability_name, request):
        key = self._key(capability_name, request)

        with self._lock:
            self._authorized.add(key)

        return True

    def consume(self, capability_name, request):
        key = self._key(capability_name, request)

        with self._lock:
            if key not in self._authorized:
                return False

            self._authorized.remove(key)
            return True
"""


def governed_write(runtime, path, content):
    result = runtime.development_service.development_interface.execute(
        "write",
        {
            "path": path,
            "content": content,
        },
    )

    print("GOVERNED WRITE:", result.ok, result.code, result.message)

    if result.data is not None:
        print(result.data)

    if not result.ok:
        raise SystemExit(1)


runtime = CapabilityRuntime(
    workspace_root=PROJECT_ROOT,
    permissions={"filesystem.read", "filesystem.write", "git.read"},
)

runtime.development_service.set_development_mode(True)

governed_write(
    runtime,
    "modules/capabilities/external_authorization.py",
    AUTHORIZATION_FILE,
)