import pytest

from ui.asset_models import VisualAsset
from ui.asset_registry import VisualAssetRegistry


def make_asset(
    asset_id="zoey.primary",
    role="assistant",
    active=False,
):
    return VisualAsset(
        asset_id=asset_id,
        role=role,
        file_path="assets/zoey-primary.png",
        source_type="user_artwork",
        provenance="ZebBravo Visual Gateway",
        active=active,
    )


def test_register_and_get_asset():
    registry = VisualAssetRegistry()
    asset = make_asset()

    registry.register(asset)

    assert registry.get("zoey.primary") == asset


def test_missing_asset_returns_none():
    registry = VisualAssetRegistry()

    assert registry.get("does.not.exist") is None


def test_assets_are_returned_in_stable_order():
    registry = VisualAssetRegistry(
        [
            make_asset("zeta", "other"),
            make_asset("alpha", "other"),
        ]
    )

    assert [asset.asset_id for asset in registry.list_assets()] == [
        "alpha",
        "zeta",
    ]


def test_duplicate_asset_id_is_rejected():
    registry = VisualAssetRegistry()
    registry.register(make_asset())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(make_asset())


def test_invalid_asset_type_is_rejected():
    registry = VisualAssetRegistry()

    with pytest.raises(TypeError, match="VisualAsset"):
        registry.register("not an asset")


def test_get_active_returns_active_asset_for_role():
    registry = VisualAssetRegistry(
        [
            make_asset("zoey.inactive", "assistant", active=False),
            make_asset("zoey.active", "assistant", active=True),
        ]
    )

    assert registry.get_active("assistant").asset_id == "zoey.active"


def test_get_active_returns_none_when_no_active_asset_exists():
    registry = VisualAssetRegistry(
        [make_asset("zoey.inactive", "assistant", active=False)]
    )

    assert registry.get_active("assistant") is None


def test_multiple_active_assets_for_one_role_are_rejected():
    registry = VisualAssetRegistry(
        [
            make_asset("zoey.one", "assistant", active=True),
            make_asset("zoey.two", "assistant", active=True),
        ]
    )

    with pytest.raises(ValueError, match="Multiple active"):
        registry.get_active("assistant")
