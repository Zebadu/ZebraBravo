import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from json_continuity_repository import JsonContinuityRepository
from continuity_service import ContinuityService


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


def test_project_continuity_file_exists():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = (
        project_root
        / "data"
        / "project_continuity_spec.json"
    )

    assert continuity_file.exists()


def test_project_continuity_is_valid():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = (
        project_root
        / "data"
        / "project_continuity_spec.json"
    )

    with open(continuity_file, "r", encoding="utf-8") as file:
        continuity = json.load(file)

    assert continuity["project"] == "ZebraBravo"
    assert continuity["continuity_version"] == 2


def test_zoey_continuity_foundation_exists():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = (
        project_root
        / "data"
        / "project_continuity_spec.json"
    )

    with open(continuity_file, "r", encoding="utf-8") as file:
        continuity = json.load(file)

    assert continuity["zoey"]["status"] == (
        "foundational_project_entity"
    )
    assert "Zoey is the heart and soul of the ZebraBravo project." in (
        continuity["zoey"]["principles"]
    )


def test_continuity_repository_loads_record():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        continuity = repository.load()

        assert continuity["project"] == "ZebraBravo"
        assert continuity["continuity_version"] == 2
        assert continuity["checkpoint"]["verified_tests"]["passed"] == 61
        assert continuity["zoey"]["status"] == (
            "foundational_project_entity"
        )
    finally:
        continuity_file.unlink()


def test_continuity_service_gets_current_record():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ContinuityService(repository)

        continuity = service.get_current()

        assert continuity["project"] == "ZebraBravo"
        assert continuity["continuity_version"] == 2
        assert continuity["next_action"] == (
            "Design and test structured Zoey continuity alongside automatic Project Continuity checkpoint creation and retrieval."
        )
        assert continuity["zoey"]["status"] == (
            "foundational_project_entity"
        )
    finally:
        continuity_file.unlink()


def test_continuity_service_updates_next_action():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ContinuityService(repository)

        new_action = "Test automatic continuity checkpoint updates."

        service.update_next_action(new_action)

        continuity = service.get_current()

        assert continuity["next_action"] == new_action
    finally:
        continuity_file.unlink()


def test_continuity_service_updates_checkpoint():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ContinuityService(repository)

        new_checkpoint = {
            "date": "2026-08-17",
            "summary": "Checkpoint update verified.",
            "verified_tests": {
                "passed": 61,
                "subtests_passed": 9,
                "failures": 0,
            },
        }

        service.update_checkpoint(new_checkpoint)

        continuity = service.get_current()

        assert continuity["checkpoint"] == new_checkpoint
    finally:
        continuity_file.unlink()