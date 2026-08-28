import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from ui.asset_models import VisualAsset  # noqa: E402
from ui.asset_registry import VisualAssetRegistry  # noqa: E402
from ui.visual_contracts import VisualRequest  # noqa: E402
from ui.visual_gateway import VisualGateway  # noqa: E402


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
        provenance="ZebraBravo Visual Gateway",
        approval_state="approved" if active else "unapproved",
        active=active,
    )


def make_gateway(*assets):
    return VisualGateway(
        VisualAssetRegistry(assets)
    )


def test_get_asset_returns_registered_asset():
    asset = make_asset()

    result = make_gateway(asset).execute(
        {
            "operation": "get_asset",
            "asset_id": "zoey.primary",
        }
    )

    assert result.ok is True
    assert result.data == asset


def test_get_asset_accepts_visual_request():
    asset = make_asset()

    result = make_gateway(asset).execute(
        VisualRequest(
            operation="get_asset",
            asset_id="zoey.primary",
        )
    )

    assert result.ok is True
    assert result.data == asset


def test_get_missing_asset_returns_failure():
    result = make_gateway().execute(
        {
            "operation": "get_asset",
            "asset_id": "missing.asset",
        }
    )

    assert result.ok is False
    assert result.code == "asset_not_found"


def test_list_assets_returns_registered_assets():
    first = make_asset("alpha", "assistant")
    second = make_asset("beta", "system")

    result = make_gateway(first, second).execute(
        {
            "operation": "list_assets",
        }
    )

    assert result.ok is True
    assert result.data == (first, second)


def test_get_active_returns_active_role_asset():
    inactive = make_asset(
        "zoey.inactive",
        "assistant",
        active=False,
    )
    active = make_asset(
        "zoey.active",
        "assistant",
        active=True,
    )

    result = make_gateway(inactive, active).execute(
        {
            "operation": "get_active",
            "role": "assistant",
        }
    )

    assert result.ok is True
    assert result.data == active


def test_get_active_returns_failure_when_no_active_asset_exists():
    result = make_gateway(
        make_asset(
            "zoey.inactive",
            "assistant",
            active=False,
        )
    ).execute(
        {
            "operation": "get_active",
            "role": "assistant",
        }
    )

    assert result.ok is False
    assert result.code == "active_asset_not_found"


def test_multiple_active_assets_are_reported_as_failure():
    first = make_asset(
        "zoey.one",
        "assistant",
        active=True,
    )
    second = make_asset(
        "zoey.two",
        "assistant",
        active=True,
    )

    result = make_gateway(first, second).execute(
        {
            "operation": "get_active",
            "role": "assistant",
        }
    )

    assert result.ok is False
    assert result.code == "multiple_active_assets"


@pytest.mark.parametrize(
    "payload",
    [
        None,
        "not a mapping",
        123,
        [],
    ],
)
def test_invalid_request_types_are_rejected(payload):
    result = make_gateway().execute(payload)

    assert result.ok is False
    assert result.code == "invalid_request"


def test_missing_operation_is_rejected():
    result = make_gateway().execute({})

    assert result.ok is False
    assert result.code == "invalid_request"


def test_unknown_operation_is_rejected():
    result = make_gateway().execute(
        {
            "operation": "something_new",
        }
    )

    assert result.ok is False
    assert result.code == "invalid_request"


def test_get_asset_without_id_is_rejected():
    result = make_gateway().execute(
        {
            "operation": "get_asset",
        }
    )

    assert result.ok is False
    assert result.code == "invalid_request"


def test_get_active_without_role_is_rejected():
    result = make_gateway().execute(
        {
            "operation": "get_active",
        }
    )

    assert result.ok is False
    assert result.code == "invalid_request"


def test_gateway_requires_asset_registry():
    with pytest.raises(
        TypeError,
        match="VisualGateway requires",
    ):
        VisualGateway("not a registry")