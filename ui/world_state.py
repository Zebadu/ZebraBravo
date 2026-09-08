from dataclasses import dataclass


VALID_WORLD_STATES = frozenset(
    {
        "sleeping",
        "awakening",
        "aware",
        "bridge_available",
        "communicating",
        "door_opening",
        "gateway_active",
    }
)


@dataclass(frozen=True)
class VisualWorldState:
    """Describes the current state of the living ZebraBravo visual world."""

    state: str = "sleeping"

    def __post_init__(self):
        if self.state not in VALID_WORLD_STATES:
            raise ValueError(
                f"Unsupported visual world state: {self.state}"
            )