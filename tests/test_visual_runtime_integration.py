import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime  # noqa: E402
from ui.asset_models import VisualAsset  # noqa: E402
from ui.asset_registry import VisualAssetRegistry  # noqa: E402
from ui.visual_gateway import VisualGateway  # noqa: E402


class VisualRuntimeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.asset = VisualAsset(
            asset_id="zoey.primary",
            role="assistant",
            file_path="assets/zoey-primary.png",
            source_type="user_artwork",
            provenance="ZebraBravo Visual Gateway",
            approval_state="approved",
            active=True,
        )

        registry = VisualAssetRegistry([self.asset])
        visual_gateway = VisualGateway(registry)

        self.runtime = CapabilityRuntime(
            permissions={"visual.read"},
            dependencies={
                "visual_gateway": visual_gateway,
            },
        )

    def test_visual_request_travels_through_full_runtime_spine(self):
        result = self.runtime.execute(
            "visual",
            {
                "operation": "get_active",
                "role": "assistant",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data, self.asset)

    def test_visual_request_can_list_assets_through_runtime(self):
        result = self.runtime.execute(
            "visual",
            {
                "operation": "list_assets",
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data, (self.asset,))

    def test_visual_requires_explicit_permission(self):
        registry = VisualAssetRegistry([self.asset])
        visual_gateway = VisualGateway(registry)

        runtime = CapabilityRuntime(
            dependencies={
                "visual_gateway": visual_gateway,
            },
        )

        result = runtime.execute(
            "visual",
            {
                "operation": "get_active",
                "role": "assistant",
            },
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "permission_denied")

    def test_visual_dependency_is_passed_through_context(self):
        visual_gateway = self.runtime.context.get_dependency(
            "visual_gateway"
        )

        self.assertIsInstance(
            visual_gateway,
            VisualGateway,
        )


if __name__ == "__main__":
    unittest.main()