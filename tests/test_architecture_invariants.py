from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "modules"))

from architecture.invariants import SPECIALIST_OWNERSHIP_INVARIANT


def test_specialist_ownership_invariant():
    invariant = SPECIALIST_OWNERSHIP_INVARIANT

    assert invariant["rule"] == (
        "ONE PURPOSE -> ONE SPECIALIST SYSTEM -> ONE OWNER"
    )

    boundaries = invariant["boundaries"]

    assert boundaries["vision"]["owner"] == "BionicVisual Vision"
    assert boundaries["generation"]["owner"] == "BionicVisual Generation"
    assert boundaries["visual_tools"]["owner"] == "ZebraBravo VisualGateway"


def test_implementation_does_not_define_specialist_identity():
    invariant = SPECIALIST_OWNERSHIP_INVARIANT

    assert "Shared implementation technology does not imply shared " \
           "purpose, ownership, or architecture." == \
           invariant["implementation_rule"]


def test_qwen_is_an_implementation_engine_not_a_top_level_capability():
    invariant = SPECIALIST_OWNERSHIP_INVARIANT

    assert "Qwen3-VL" in invariant["engine_rule"]
    assert "subordinate to their specialist system" in invariant["engine_rule"]
