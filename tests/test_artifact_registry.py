import pytest

from modules.artifact import ArtifactRecord
from modules.artifact_registry import ArtifactRegistry


def make_artifact(
    artifact_id="artifact.one",
    name="Test Artifact",
):
    return ArtifactRecord(
        artifact_id=artifact_id,
        name=name,
        provider="test",
        reference=f"memory://{artifact_id}",
        content_type="text/plain",
        size=123,
    )


def test_register_and_get_artifact():
    registry = ArtifactRegistry()
    artifact = make_artifact()

    registry.register(artifact)

    assert registry.get("artifact.one") == artifact


def test_missing_artifact_returns_none():
    registry = ArtifactRegistry()

    assert registry.get("does.not.exist") is None


def test_artifacts_are_returned_in_stable_order():
    registry = ArtifactRegistry(
        [
            make_artifact("zeta"),
            make_artifact("alpha"),
        ]
    )

    assert [artifact.artifact_id for artifact in registry.list_artifacts()] == [
        "alpha",
        "zeta",
    ]


def test_duplicate_artifact_id_is_rejected():
    registry = ArtifactRegistry()
    registry.register(make_artifact())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(make_artifact())


def test_invalid_artifact_type_is_rejected():
    registry = ArtifactRegistry()

    with pytest.raises(TypeError, match="Artifact must be an ArtifactRecord"):
        registry.register("not an artifact")


def test_empty_registry_has_zero_count():
    registry = ArtifactRegistry()

    assert registry.count() == 0
    assert registry.list_artifacts() == ()
