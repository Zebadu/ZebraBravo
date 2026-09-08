import pytest

from ui.world_state import VALID_WORLD_STATES, VisualWorldState


def test_default_world_state_is_sleeping():
    state = VisualWorldState()

    assert state.state == "sleeping"


def test_valid_world_states_are_accepted():
    for value in VALID_WORLD_STATES:
        state = VisualWorldState(state=value)

        assert state.state == value


def test_invalid_world_state_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported visual world state: not_a_real_state",
    ):
        VisualWorldState(state="not_a_real_state")


def test_world_state_is_immutable():
    state = VisualWorldState()

    with pytest.raises(AttributeError):
        state.state = "awake"