import pytest

from ui.visual_contracts import (
    VALID_VISUAL_OPERATIONS,
    VisualRequest,
)


def test_valid_visual_operations_are_defined():
    assert VALID_VISUAL_OPERATIONS == {
        "get_asset",
        "list_assets",
        "get_active",
    }


def test_get_asset_request_is_valid():
    request = VisualRequest(
        operation="get_asset",
        asset_id="zoey.primary",
    )

    assert request.operation == "get_asset"
    assert request.asset_id == "zoey.primary"


def test_list_assets_request_is_valid():
    request = VisualRequest(operation="list_assets")

    assert request.operation == "list_assets"


def test_get_active_request_is_valid():
    request = VisualRequest(
        operation="get_active",
        role="assistant",
    )

    assert request.role == "assistant"


def test_unknown_operation_is_rejected():
    with pytest.raises(ValueError, match="Unsupported visual operation"):
        VisualRequest(operation="explode_everything")


def test_missing_operation_is_rejected():
    with pytest.raises(ValueError, match="operation is required"):
        VisualRequest(operation="")


def test_get_asset_requires_asset_id():
    with pytest.raises(ValueError, match="asset ID is required"):
        VisualRequest(operation="get_asset")


def test_get_active_requires_role():
    with pytest.raises(ValueError, match="role is required"):
        VisualRequest(operation="get_active")


def test_mapping_can_create_get_asset_request():
    request = VisualRequest.from_mapping(
        {
            "operation": "get_asset",
            "asset_id": "zoey.primary",
        }
    )

    assert request.asset_id == "zoey.primary"


def test_mapping_can_create_list_request():
    request = VisualRequest.from_mapping(
        {
            "operation": "list_assets",
        }
    )

    assert request.operation == "list_assets"


def test_non_mapping_request_is_rejected():
    with pytest.raises(TypeError, match="must be a mapping"):
        VisualRequest.from_mapping("not a mapping")


def test_visual_request_is_immutable():
    request = VisualRequest(operation="list_assets")

    with pytest.raises(AttributeError):
        request.operation = "get_asset"
