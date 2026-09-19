import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.visual_observation import VisualObservation  # noqa: E402


def test_visual_observation_from_capture():
    capture = {
        "title": "Blender",
        "size": (800, 600),
        "format": "BGRA",
        "bytes": b"pixel-data",
    }

    observation = VisualObservation.from_capture(capture)

    assert observation.source == "desktop"
    assert observation.title == "Blender"
    assert observation.width == 800
    assert observation.height == 600
    assert observation.format == "BGRA"
    assert observation.data == b"pixel-data"
    assert observation.provenance == "local_desktop_capture"
    assert observation.observation_id.startswith("desktop-")
    assert observation.captured_at


def test_visual_observation_requires_bytes():
    try:
        VisualObservation(
            observation_id="test-1",
            source="desktop",
            title="Blender",
            width=800,
            height=600,
            format="BGRA",
            data="not-bytes",
            captured_at="2026-09-18T00:00:00+00:00",
        )
    except TypeError as error:
        assert str(error) == "Observation data must be bytes."
    else:
        raise AssertionError("Expected TypeError.")


def test_visual_observation_requires_positive_dimensions():
    try:
        VisualObservation(
            observation_id="test-1",
            source="desktop",
            title="Blender",
            width=0,
            height=600,
            format="BGRA",
            data=b"pixel-data",
            captured_at="2026-09-18T00:00:00+00:00",
        )
    except ValueError as error:
        assert str(error) == "Observation dimensions must be positive."
    else:
        raise AssertionError("Expected ValueError.")