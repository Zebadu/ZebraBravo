from collections.abc import Mapping

from capabilities.contracts import CapabilityResult
from ui.asset_registry import VisualAssetRegistry
from ui.visual_contracts import VisualRequest


class VisualGateway:
    """Controlled gateway for resolving ZebraBravo visual assets."""

    def __init__(self, registry: VisualAssetRegistry):
        if not isinstance(registry, VisualAssetRegistry):
            raise TypeError("VisualGateway requires a VisualAssetRegistry.")

        self.registry = registry

    def execute(self, request):
        try:
            visual_request = (
                request
                if isinstance(request, VisualRequest)
                else VisualRequest.from_mapping(request)
            )
        except (TypeError, ValueError) as error:
            return self._failure(
                "invalid_request",
                str(error),
            )

        if visual_request.operation == "get_asset":
            return self._get_asset(visual_request)

        if visual_request.operation == "list_assets":
            return CapabilityResult(
                ok=True,
                data=self.registry.list_assets(),
            )

        if visual_request.operation == "get_active":
            return self._get_active(visual_request)

        return self._failure(
            "unsupported_operation",
            f"Unsupported visual operation: {visual_request.operation}",
        )

    def _get_asset(self, request: VisualRequest):
        asset = self.registry.get(request.asset_id)

        if asset is None:
            return self._failure(
                "asset_not_found",
                f"Visual asset not found: {request.asset_id}",
            )

        return CapabilityResult(
            ok=True,
            data=asset,
        )

    def _get_active(self, request: VisualRequest):
        try:
            asset = self.registry.get_active(request.role)
        except ValueError as error:
            return self._failure(
                "multiple_active_assets",
                str(error),
            )

        if asset is None:
            return self._failure(
                "active_asset_not_found",
                f"No active visual asset found for role: {request.role}",
            )

        return CapabilityResult(
            ok=True,
            data=asset,
        )

    def _failure(self, code, message):
        return CapabilityResult(
            ok=False,
            message=message,
            code=code,
        )
