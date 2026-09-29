import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / 'modules'
sys.path.insert(0, str(MODULES_DIR))

from modules.artifact import ArtifactRecord
from modules.artifact_registry import ArtifactRegistry
from assistant import Assistant


def test_assistant_can_retrieve_registered_artifact(tmp_path):
    registry = ArtifactRegistry()

    artifact = ArtifactRecord(
        artifact_id="artifact-001",
        name="First ZebraBravo Artifact",
        provider="test",
        reference="test://artifact-001",
        content_type="text/plain",
        size=42,
    )

    registry.register(artifact)

    assistant = Assistant(
        tmp_path,
        artifact_registry=registry,
    )

    assert assistant.artifact_registry.get("artifact-001") == artifact
