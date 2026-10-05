"""Non-negotiable architectural boundaries for ZebraBravo and BionicVisual."""

SPECIALIST_OWNERSHIP_INVARIANT = {
    "rule": "ONE PURPOSE -> ONE SPECIALIST SYSTEM -> ONE OWNER",
    "boundaries": {
        "vision": {
            "purpose": "visual inspection and understanding",
            "owner": "BionicVisual Vision",
        },
        "generation": {
            "purpose": "image creation and generation",
            "owner": "BionicVisual Generation",
        },
        "visual_tools": {
            "purpose": "governed access to visual applications and tools",
            "owner": "ZebraBravo VisualGateway",
        },
    },
    "implementation_rule": (
        "Shared implementation technology does not imply shared "
        "purpose, ownership, or architecture."
    ),
    "engine_rule": (
        "Implementation engines such as Qwen3-VL are subordinate to "
        "their specialist system and are not themselves top-level "
        "specialist capabilities."
    ),
}
