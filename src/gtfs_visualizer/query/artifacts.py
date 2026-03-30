from __future__ import annotations

from pathlib import Path

from gtfs_visualizer.artifacts import (
    ArtifactBundleError,
    ValidatedArtifactBundle,
    load_validated_artifact_bundle,
)

QueryArtifactError = ArtifactBundleError
QueryBundle = ValidatedArtifactBundle


def load_query_bundle(artifacts_dir: Path) -> QueryBundle:
    return load_validated_artifact_bundle(artifacts_dir)
