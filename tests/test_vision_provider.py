from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "modules"))

from vision.provider import VisionProvider


class FakeVisionProvider:
    def describe(self, observation):
        return "Test visual description."


def test_vision_provider_contract():
    provider = FakeVisionProvider()
    assert isinstance(provider, VisionProvider)