from dataclasses import dataclass


VALID_SOURCE_TYPES = frozenset(
    {
        "user_artwork",
        "generated",
        "system",
        "imported",
    }
)

VALID_APPROVAL_STATES = frozenset(
    {
        "unapproved",
        "approved",
        "retired",
    }
)


@dataclass(frozen=True)
class VisualAsset:
    """Describes a governed visual asset known to ZebraBravo."""

    asset_id: str
    role: str
    file_path: str
    source_type: str
    version: str = "1.0.0"
    provenance: str = ""
    approval_state: str = "unapproved"
    active: bool = False

    def __post_init__(self):
        if not self.asset_id:
            raise ValueError("Visual asset ID is required.")

        if not self.role:
            raise ValueError("Visual asset role is required.")

        if not self.file_path:
            raise ValueError("Visual asset file path is required.")

        if self.source_type not in VALID_SOURCE_TYPES:
            raise ValueError(
                f"Unsupported visual asset source type: {self.source_type}"
            )

        if self.approval_state not in VALID_APPROVAL_STATES:
            raise ValueError(
                f"Unsupported visual asset approval state: "
                f"{self.approval_state}"
            )
