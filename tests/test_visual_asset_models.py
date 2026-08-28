import pytest

from ui.asset_models import (
    VALID_APPROVAL_STATES,
    VALID_SOURCE_TYPES,
    VisualAsset,
)


def make_asset(**overrides):
    values = {
        "asset_id": "zoey.primary",
        "role": "assistant",
        "file_path": "assets/zoey-primary.png",
        "source_type": "user_artwork",
    }
    values.update(overrides)
    return VisualAsset(**values)


def test_valid_source_types_are_defined():
    assert VALID_SOURCE_TYPES == {
        "user_artwork",
        "generated",
        "system",
        "imported",
    }


def test_valid_approval_states_are_defined():
    assert VALID_APPROVAL_STATES == {
        "unapproved",
        "approved",
        "retired",
    }


@pytest.mark.parametrize(
    "source_type",
    [
        "user_artwork",
        "generated",
        "system",
        "imported",
    ],
)
def test_valid_source_type_is_accepted(source_type):
    asset = make_asset(source_type=source_type)

    assert asset.source_type == source_type


@pytest.mark.parametrize(
    "approval_state",
    [
        "unapproved",
        "approved",
        "retired",
    ],
)
def test_valid_approval_state_is_accepted(approval_state):
    asset = make_asset(approval_state=approval_state)

    assert asset.approval_state == approval_state


def test_unknown_source_type_is_rejected():
    with pytest.raises(ValueError, match="Unsupported visual asset source type"):
        make_asset(source_type="mystery")


def test_unknown_approval_state_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported visual asset approval state",
    ):
        make_asset(approval_state="maybe")


def test_empty_asset_id_is_rejected():
    with pytest.raises(ValueError, match="asset ID is required"):
        make_asset(asset_id="")


def test_empty_role_is_rejected():
    with pytest.raises(ValueError, match="role is required"):
        make_asset(role="")


def test_empty_file_path_is_rejected():
    with pytest.raises(ValueError, match="file path is required"):
        make_asset(file_path="")


def test_visual_asset_is_immutable():
    asset = make_asset()

    with pytest.raises(AttributeError):
        asset.role = "something-else"


def test_approved_active_asset_is_accepted():
    asset = make_asset(
        approval_state="approved",
        active=True,
    )

    assert asset.approval_state == "approved"
    assert asset.active is True


def test_unapproved_active_asset_is_rejected():
    with pytest.raises(
        ValueError,
        match="Active visual asset must be approved",
    ):
        make_asset(
            approval_state="unapproved",
            active=True,
        )


def test_retired_active_asset_is_rejected():
    with pytest.raises(
        ValueError,
        match="Active visual asset must be approved",
    ):
        make_asset(
            approval_state="retired",
            active=True,
        )


def test_unapproved_inactive_asset_is_accepted():
    asset = make_asset(
        approval_state="unapproved",
        active=False,
    )

    assert asset.approval_state == "unapproved"
    assert asset.active is False


def test_retired_inactive_asset_is_accepted():
    asset = make_asset(
        approval_state="retired",
        active=False,
    )

    assert asset.approval_state == "retired"
    assert asset.active is False