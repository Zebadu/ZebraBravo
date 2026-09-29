from collections.abc import Iterable

from modules.artifact import ArtifactRecord


class ArtifactRegistry:
    """In-memory registry of digital artifacts known to ZebraBravo."""

    def __init__(self, artifacts: Iterable[ArtifactRecord] = ()):
        self._artifacts: dict[str, ArtifactRecord] = {}
        for artifact in artifacts:
            self.register(artifact)

    def register(self, artifact: ArtifactRecord) -> None:
        if not isinstance(artifact, ArtifactRecord):
            raise TypeError("Artifact must be an ArtifactRecord.")
        if artifact.artifact_id in self._artifacts:
            raise ValueError(
                f"Artifact already registered: {artifact.artifact_id}"
            )
        self._artifacts[artifact.artifact_id] = artifact

    def get(self, artifact_id: str) -> ArtifactRecord | None:
        return self._artifacts.get(artifact_id)

    def list_artifacts(self) -> tuple[ArtifactRecord, ...]:
        return tuple(
            self._artifacts[artifact_id]
            for artifact_id in sorted(self._artifacts)
        )

    def count(self) -> int:
        return len(self._artifacts)
