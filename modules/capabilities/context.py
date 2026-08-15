from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class CapabilityContext:
    workspace_root: Path | None = None
    dependencies: Mapping[str, object] = field(default_factory=dict)
    permissions: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self):
        object.__setattr__(self, "dependencies", MappingProxyType(dict(self.dependencies)))
        object.__setattr__(self, "permissions", frozenset(self.permissions))

    def get_dependency(self, name):
        return self.dependencies.get(name)
