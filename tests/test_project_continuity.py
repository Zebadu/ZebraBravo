import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from json_continuity_repository import JsonContinuityRepository
from continuity_service import ContinuityService
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
    assert continuity["continuity_version"] == 3


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
    assert "personality" in continuity["zoey"]
    assert "warm" in continuity["zoey"]["personality"]["traits"]
    assert "witty" in continuity["zoey"]["personality"]["traits"]
    assert "humorous" in continuity["zoey"]["personality"]["traits"]
    assert "Zoey is the heart and soul of the ZebraBravo project." in (
        continuity["zoey"]["personality"]["principles"]
    )


def test_continuity_repository_loads_record():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        continuity = repository.load()

        assert continuity["project"] == "ZebraBravo"
        assert continuity["continuity_version"] == 3
        assert continuity["checkpoint"]["verified_tests"]["passed"] == 61
        assert continuity["zoey"]["status"] == (
            "foundational_project_entity"
        )
        assert "personality" in continuity["zoey"]
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
        assert continuity["continuity_version"] == 3
        assert continuity["next_action"] == (
            "Design and test structured Zoey personality continuity and controlled domain updates."
        )
        assert continuity["zoey"]["status"] == (
            "foundational_project_entity"
        )
        assert "personality" in continuity["zoey"]
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


def test_zoey_continuity_service_gets_current():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ZoeyContinuityService(repository)

        zoey = service.get_current()

        assert zoey["status"] == (
            "foundational_project_entity"
        )
        assert "personality" in zoey
        assert "warm" in zoey["personality"]["traits"]
        assert "witty" in zoey["personality"]["traits"]
    finally:
        continuity_file.unlink()


def test_zoey_continuity_service_updates_field():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ZoeyContinuityService(repository)

        new_status = "actively_evolving_project_entity"

        service.update_field("status", new_status)

        zoey = service.get_current()

        assert zoey["status"] == new_status
    finally:
        continuity_file.unlink()


def test_zoey_continuity_service_rejects_unknown_field():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ZoeyContinuityService(repository)

        try:
            service.update_field(
                "unknown_field",
                "should not be accepted",
            )
            assert False
        except ValueError as error:
            assert str(error) == (
                "Unknown Zoey continuity field: unknown_field"
            )
    finally:
        continuity_file.unlink()


def test_zoey_personality_domain_is_structured():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ZoeyContinuityService(repository)

        zoey = service.get_current()
        personality = zoey["personality"]

        assert isinstance(personality, dict)
        assert isinstance(personality["traits"], list)
        assert isinstance(personality["principles"], list)
        assert "analytical" in personality["traits"]
        assert "ambitious" in personality["traits"]
        assert "disciplined" in personality["traits"]
        assert "responsible" in personality["traits"]
    finally:
        continuity_file.unlink()


def test_zoey_continuity_service_gets_personality():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ZoeyContinuityService(repository)

        personality = service.get_personality()

        assert isinstance(personality, dict)
        assert "traits" in personality
        assert "principles" in personality
        assert "warm" in personality["traits"]
    finally:
        continuity_file.unlink()


def test_zoey_continuity_service_adds_personality_trait():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ZoeyContinuityService(repository)

        service.update_personality_trait("curious")

        personality = service.get_personality()

        assert "curious" in personality["traits"]
    finally:
        continuity_file.unlink()


def test_zoey_continuity_service_does_not_duplicate_personality_trait():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ZoeyContinuityService(repository)

        service.update_personality_trait("curious")
        service.update_personality_trait("curious")

        personality = service.get_personality()

        assert personality["traits"].count("curious") == 1
    finally:
        continuity_file.unlink()


def test_zoey_continuity_service_rejects_invalid_personality_trait():
    project_root = Path(__file__).resolve().parent.parent
    continuity_file = create_test_continuity_file(project_root)

    try:
        repository = JsonContinuityRepository(continuity_file)
        service = ZoeyContinuityService(repository)

        try:
            service.update_personality_trait("")
            assert False
        except ValueError as error:
            assert str(error) == (
                "Zoey personality trait cannot be empty."
            )
    finally:
        continuity_file.unlink()