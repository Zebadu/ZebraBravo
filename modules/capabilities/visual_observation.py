from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class VisualObservation:
    """Ephemeral, local representation of something ZebraBravo observed."""

    observation_id: str
    source: str
    title: str
    width: int
    height: int
    format: str
    data: bytes
    captured_at: str
    provenance: str = "local_desktop_capture"

    def __post_init__(self):
        if not self.observation_id:
            raise ValueError("Observation ID is required.")

        if not self.source:
            raise ValueError("Observation source is required.")

        if not self.title:
            raise ValueError("Observation title is required.")

        if self.width <= 0 or self.height <= 0:
            raise ValueError("Observation dimensions must be positive.")

        if not self.format:
            raise ValueError("Observation format is required.")

        if not isinstance(self.data, bytes):
            raise TypeError("Observation data must be bytes.")

        if not self.captured_at:
            raise ValueError("Observation timestamp is required.")

    @classmethod
    def from_capture(cls, capture):
        captured_at = datetime.now(timezone.utc).isoformat()
        width, height = capture["size"]

        return cls(
            observation_id=f"desktop-{captured_at}",
            source="desktop",
            title=capture["title"],
            width=width,
            height=height,
            format=capture["format"],
            data=capture["bytes"],
            captured_at=captured_at,
        )