from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactRecord:
    """Describes a digital artifact known to ZebraBravo."""

    artifact_id: str
    name: str
    provider: str
    reference: str
    content_type: str
    size: int
    created_at: str = ""
    updated_at: str = ""
    provenance: str = ""
    integrity: str = ""

    def __post_init__(self):
        if not self.artifact_id:
            raise ValueError("Artifact ID is required.")

        if not self.name:
            raise ValueError("Artifact name is required.")

        if not self.provider:
            raise ValueError("Artifact provider is required.")

        if not self.reference:
            raise ValueError("Artifact reference is required.")

        if not self.content_type:
            raise ValueError("Artifact content type is required.")

        if self.size < 0:
            raise ValueError("Artifact size cannot be negative.")
