from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class Intent:
    """A validated description of what the user wants to accomplish."""

    name: str
    capability: str
    operation: str
    parameters: Mapping[str, Any]