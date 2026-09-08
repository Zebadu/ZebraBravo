from dataclasses import dataclass
from typing import Any, Mapping


VALID_INTENT_ROUTES = frozenset(
    {
        "capability",
        "development",
    }
)


@dataclass(frozen=True)
class Intent:
    """A validated description of what the user wants to accomplish."""

    name: str
    capability: str
    operation: str
    parameters: Mapping[str, Any]
    route: str = "capability"

    def __post_init__(self):
        if self.route not in VALID_INTENT_ROUTES:
            raise ValueError(
                f"Unsupported intent route: {self.route}"
            )