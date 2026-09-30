from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class GovernanceContext:
    """Immutable authority and mission context for governed execution."""

    principal: str = ""
    authority: str = ""
    mission_id: str = ""
    resource_scope: tuple[str, ...] = ()
    authorization_provenance: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.principal, str):
            raise TypeError("principal must be a string.")
        if not isinstance(self.authority, str):
            raise TypeError("authority must be a string.")
        if not isinstance(self.mission_id, str):
            raise TypeError("mission_id must be a string.")
        if not isinstance(self.resource_scope, tuple):
            object.__setattr__(self, "resource_scope", tuple(self.resource_scope))
        if not all(isinstance(item, str) for item in self.resource_scope):
            raise TypeError("resource_scope entries must be strings.")
        object.__setattr__(
            self,
            "authorization_provenance",
            MappingProxyType(dict(self.authorization_provenance)),
        )
