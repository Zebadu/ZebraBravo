from collections.abc import Iterable

from ui.asset_models import VisualAsset


class VisualAssetRegistry:
    """In-memory registry of ZebraBravo visual assets."""

    def __init__(self, assets: Iterable[VisualAsset] = ()):
        self._assets = {}

        for asset in assets:
            self.register(asset)

    def register(self, asset: VisualAsset):
        if not isinstance(asset, VisualAsset):
            raise TypeError("Asset must be a VisualAsset.")

        if asset.asset_id in self._assets:
            raise ValueError(f"Visual asset already registered: {asset.asset_id}")

        self._assets[asset.asset_id] = asset

    def get(self, asset_id: str):
        return self._assets.get(asset_id)

    def list_assets(self):
        return tuple(
            self._assets[asset_id]
            for asset_id in sorted(self._assets)
        )

    def get_active(self, role: str):
        matches = [
            asset
            for asset in self._assets.values()
            if asset.role == role and asset.active
        ]

        if not matches:
            return None

        if len(matches) > 1:
            raise ValueError(
                f"Multiple active visual assets found for role: {role}"
            )

        return matches[0]
