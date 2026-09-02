import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.development_bridge import DevelopmentBridge  # noqa: E402
from capabilities.runtime import CapabilityRuntime  # noqa: E402


class DevelopmentRuntimeBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()

        (self.root / "hello.txt").write_text(
            "Hello from ZebraBravo.",
            encoding="utf-8",
        )

        self.runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read"},
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_runtime_exposes_development_bridge(self):
        self.assertIsInstance(
            self.runtime.development_bridge,
            DevelopmentBridge,
        )

    def test_runtime_bridge_uses_development_service(self):
        self.assertIs(
            self.runtime.development_bridge.development_service,
            self.runtime.development_service,
        )

    def test_runtime_bridge_is_local_only(self):
        self.assertEqual(
            self.runtime.development_bridge.host,
            "127.0.0.1",
        )

    def test_runtime_bridge_is_not_started_automatically(self):
        self.assertIsNone(
            self.runtime.development_bridge.address,
        )

        self.assertFalse(
            self.runtime.development_bridge.is_running,
        )


if __name__ == "__main__":
    unittest.main()