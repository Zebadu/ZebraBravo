import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.development import DevelopmentInterface  # noqa: E402
from capabilities.development_protocol import DevelopmentProtocol  # noqa: E402
from capabilities.mcp_adapter import McpDevelopmentAdapter  # noqa: E402
from capabilities.runtime import CapabilityRuntime  # noqa: E402


class McpDevelopmentAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "workspace"
        self.root.mkdir()
        (self.root / "hello.txt").write_text("Hello.", encoding="utf-8")

        runtime = CapabilityRuntime(
            workspace_root=self.root,
            permissions={"filesystem.read", "git.read"},
        )
        protocol = DevelopmentProtocol(DevelopmentInterface(runtime))
        self.adapter = McpDevelopmentAdapter(protocol)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_lists_only_read_only_tools(self):
        response = self.adapter.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

        tools = {tool["name"] for tool in response["result"]["tools"]}

        self.assertIn("read", tools)
        self.assertNotIn("write", tools)
        self.assertNotIn("test", tools)
        self.assertNotIn("development_mode", tools)

    def test_read_routes_through_development_protocol(self):
        response = self.adapter.handle(
            {
                "jsonrpc": "2.0",
                "id": "read-1",
                "method": "tools/call",
                "params": {"name": "read", "arguments": {"path": "hello.txt"}},
            }
        )

        result = response["result"]
        self.assertFalse(result["isError"])
        self.assertEqual(result["structuredContent"]["operation"], "read")
        self.assertEqual(result["structuredContent"]["data"]["content"], "Hello.")

    def test_write_cannot_be_called_through_mcp_adapter(self):
        response = self.adapter.handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "write", "arguments": {}},
            }
        )

        self.assertEqual(response["error"]["code"], -32602)


if __name__ == "__main__":
    unittest.main()
