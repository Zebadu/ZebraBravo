from typing import Any, Mapping, Protocol


class IntentReasoner(Protocol):
    """Determine structured intent information from natural language."""

    def reason(self, request: str) -> Mapping[str, Any]:
        """Return structured information suitable for IntentFormation."""
        ...
