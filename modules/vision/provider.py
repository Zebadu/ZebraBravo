from typing import Protocol, runtime_checkable

from capabilities.visual_observation import VisualObservation


@runtime_checkable
class VisionProvider(Protocol):
    """Provider-neutral interface for understanding visual observations."""

    def describe(self, observation: VisualObservation) -> str:
        """Return a textual interpretation of a visual observation."""
        ...