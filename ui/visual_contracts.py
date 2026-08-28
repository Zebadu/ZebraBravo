from dataclasses import dataclass
from typing import Mapping


VALID_VISUAL_OPERATIONS = frozenset(
    {
        "get_asset",
        "list_assets",
        "get_active",
    }
)


@dataclass(frozen=True)
class VisualRequest:
    """Structured request entering the Visual Gateway."""

    operation: str
    asset_id: str | None = None
    role: str | None = None

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation:
            raise ValueError("Visual Gateway operation is required.")

        if self.operation not in VALID_VISUAL_OPERATIONS:
            raise ValueError(
                f"Unsupported visual operation: {self.operation}"
            )

        if self.operation == "get_asset":
            if not isinstance(self.asset_id, str) or not self.asset_id:
                raise ValueError("Visual asset ID is required.")

        if self.operation == "get_active":
            if not isinstance(self.role, str) or not self.role:
                raise ValueError("Visual asset role is required.")

    @classmethod
    def from_mapping(cls, request: Mapping[str, object]):
        if not isinstance(request, Mapping):
            raise TypeError("Visual Gateway request must be a mapping.")

        return cls(
            operation=request.get("operation"),
            asset_id=request.get("asset_id"),
            role=request.get("role"),
        )
