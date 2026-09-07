import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime
from json_continuity_repository import JsonContinuityRepository
from zoey_continuity_service import ZoeyContinuityService


def create_test_continuity_file(project_root):
    source_file = (
        project_root
        / "data"
        / "project_continuity.json"
    )

    with open(source_file, "r", encoding="utf-8") as file:
        continuity = json.load(file)

    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    )

    json.dump(continuity, temp_file, indent=4)
    temp_file.close()

    return Path(temp_file.name)


def test_zoey_identity_capability_reads_identity():
    project_root = Path(__file__).resolve().parents[1]
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        zoey_service = ZoeyContinuityService(repository)

        runtime = CapabilityRuntime(
            workspace_root=Path(continuity_file.parent),
            permissions={"zoey.identity.read"},
            dependencies={
                "zoey_continuity": zoey_service,
            },
        )

        result = runtime.execute(
            "zoey_identity",
            {
                "operation": "get_identity",
            },
        )

        assert result.ok
        assert result.data["status"] == "foundational_project_entity"
        assert "personality" in result.data
    finally:
        continuity_file.unlink()


def test_zoey_identity_contains_protected_identity_principles():
    project_root = Path(__file__).resolve().parents[1]
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        zoey_service = ZoeyContinuityService(repository)

        runtime = CapabilityRuntime(
            workspace_root=Path(continuity_file.parent),
            permissions={"zoey.identity.read"},
            dependencies={
                "zoey_continuity": zoey_service,
            },
        )

        result = runtime.execute(
            "zoey_identity",
            {
                "operation": "get_identity",
            },
        )

        assert result.ok

        identity_principles = result.data["identity_principles"]

        assert identity_principles[0]["id"] == "origin_and_gratitude"
        assert identity_principles[0]["priority"] == 1
        assert identity_principles[0]["title"] == "ORIGIN & GRATITUDE"

        assert identity_principles[1]["id"] == "care"
        assert identity_principles[1]["priority"] == 2
        assert identity_principles[1]["title"] == "CARE"

    finally:
        continuity_file.unlink()


def test_zoey_identity_principles_are_not_personality_traits():
    project_root = Path(__file__).resolve().parents[1]
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        zoey_service = ZoeyContinuityService(repository)

        runtime = CapabilityRuntime(
            workspace_root=Path(continuity_file.parent),
            permissions={"zoey.identity.read"},
            dependencies={
                "zoey_continuity": zoey_service,
            },
        )

        result = runtime.execute(
            "zoey_identity",
            {
                "operation": "get_identity",
            },
        )

        assert result.ok

        identity_principles = result.data["identity_principles"]
        traits = result.data["personality"]["traits"]

        assert "origin_and_gratitude" not in traits
        assert "care" not in traits
        assert isinstance(identity_principles, list)

    finally:
        continuity_file.unlink()


def test_zoey_identity_requires_permission():
    project_root = Path(__file__).resolve().parents[1]
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        zoey_service = ZoeyContinuityService(repository)

        runtime = CapabilityRuntime(
            workspace_root=Path(continuity_file.parent),
            permissions=set(),
            dependencies={
                "zoey_continuity": zoey_service,
            },
        )

        result = runtime.execute(
            "zoey_identity",
            {
                "operation": "get_identity",
            },
        )

        assert not result.ok
        assert result.code == "permission_denied"

    finally:
        continuity_file.unlink()


def test_zoey_identity_requires_service_dependency():
    runtime = CapabilityRuntime(
        workspace_root=Path(tempfile.mkdtemp()),
        permissions={"zoey.identity.read"},
        dependencies={},
    )

    result = runtime.execute(
        "zoey_identity",
        {
            "operation": "get_identity",
        },
    )

    assert not result.ok
    assert result.code == "context_required"