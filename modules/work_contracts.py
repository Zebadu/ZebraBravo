from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

class WorkStatus(str, Enum):
    """Lifecycle states for persistent governed work."""
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(frozen=True)
class WorkRecord:
    """Durable description and state of a unit of governed work."""
    work_id: str
    name: str
    intent: Mapping[str, Any]
    status: WorkStatus = WorkStatus.QUEUED
    checkpoint: Mapping[str, Any] = field(default_factory=dict)
    next_action: str = ""
    context: Mapping[str, Any] = field(default_factory=dict)
    evidence: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.work_id.strip():
            raise ValueError("Work ID cannot be empty.")
        if not self.name.strip():
            raise ValueError("Work name cannot be empty.")
        if not isinstance(self.intent, Mapping):
            raise ValueError("Work intent must be a mapping.")
        if not isinstance(self.status, WorkStatus):
            raise ValueError("Work status must be a WorkStatus value.")
        if not isinstance(self.checkpoint, Mapping):
            raise ValueError("Work checkpoint must be a mapping.")
        if not isinstance(self.next_action, str):
            raise ValueError("Work next_action must be text.")
        if not isinstance(self.context, Mapping):
            raise ValueError("Work context must be a mapping.")
        if not isinstance(self.evidence, tuple):
            raise ValueError("Work evidence must be a tuple.")
