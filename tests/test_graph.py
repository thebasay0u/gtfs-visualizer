from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from gtfs_visualizer.artifacts import ArtifactBundleError, load_validated_artifact_bundle
from gtfs_visualizer.graph import build_graph_artifacts, serialize_graph_edges, serialize_graph_nodes

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "sample-data" / "fixtures"


def _ingest_fixture(fixture_name: str, prefix: str) -> Path:
    temp_base = REPO_ROOT / ".tmp"
    temp_base.mkdir(parents=True, exist_ok=True)
    output_dir = temp_base / f"{prefix}-{uuid.uuid4().hex}"
    output_dir.mkdir(parents=True, exist_ok=False)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gtfs_visualizer.cli",
            "ingest",
            str(FIXTURES_DIR / fixture_name),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode in {0, 1}
    return output_dir


def test_build_graph_artifacts_produces_minimal_schema_for_valid_bundle() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms005-valid")
    try:
        graph = build_graph_artifacts(load_validated_artifact_bundle(output_dir))
        nodes_payload = serialize_graph_nodes(graph)
        edges_payload = serialize_graph_edges(graph)

        assert nodes_payload["version"] == 1
        assert nodes_payload["generated_from"] == {
            "normalized_entities": "normalized_entities.json",
            "relationships": "relationships.json",
        }
        assert [node["id"] for node in nodes_payload["nodes"]] == [
            "route:R1",
            "stop:STOP1",
            "stop:STOP2",
            "trip:T1",
        ]
        assert nodes_payload["nodes"][0] == {
            "id": "route:R1",
            "type": "route",
            "entity_id": "R1",
            "label": "Route 10",
            "attributes": {
                "route_id": "R1",
                "route_short_name": "10",
                "route_long_name": "Downtown Loop",
                "route_type": 3,
            },
        }
        assert all("source_file" not in node["attributes"] for node in nodes_payload["nodes"])
        assert all("source_row" not in node["attributes"] for node in nodes_payload["nodes"])

        assert edges_payload["version"] == 1
        assert edges_payload["generated_from"] == {
            "normalized_entities": "normalized_entities.json",
            "relationships": "relationships.json",
        }
        assert [edge["id"] for edge in edges_payload["edges"]] == [
            "route_has_trip:route:R1:trip:T1",
            "trip_stops_at:trip:T1:stop:STOP1:1",
            "trip_stops_at:trip:T1:stop:STOP2:2",
        ]
        assert edges_payload["edges"][0] == {
            "id": "route_has_trip:route:R1:trip:T1",
            "type": "route_has_trip",
            "source": "route:R1",
            "target": "trip:T1",
            "attributes": {"route_id": "R1", "trip_id": "T1"},
        }
        assert edges_payload["edges"][1] == {
            "id": "trip_stops_at:trip:T1:stop:STOP1:1",
            "type": "trip_stops_at",
            "source": "trip:T1",
            "target": "stop:STOP1",
            "attributes": {"trip_id": "T1", "stop_id": "STOP1", "stop_sequence": 1},
        }
        assert all("stop_time_key" not in edge["attributes"] for edge in edges_payload["edges"])
        assert all("arrival_time" not in edge["attributes"] for edge in edges_payload["edges"])
        assert all("departure_time" not in edge["attributes"] for edge in edges_payload["edges"])
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_build_graph_artifacts_succeeds_for_warning_only_bundle() -> None:
    output_dir = _ingest_fixture("missing-shapes-feed", "ms005-warning")
    try:
        graph = build_graph_artifacts(load_validated_artifact_bundle(output_dir))

        assert [node.type for node in graph.nodes] == ["route", "stop", "stop", "trip"]
        assert [edge.type for edge in graph.edges] == [
            "route_has_trip",
            "trip_stops_at",
            "trip_stops_at",
        ]
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_load_validated_artifact_bundle_rejects_fatal_validation_outputs() -> None:
    output_dir = _ingest_fixture("invalid-relations-feed", "ms005-invalid")
    try:
        try:
            load_validated_artifact_bundle(output_dir)
        except ArtifactBundleError as exc:
            assert "invalid/raw-only" in str(exc)
        else:
            raise AssertionError("Expected ArtifactBundleError")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_graph_generation_writes_expected_artifacts() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms005-cli")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "graph", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 0
        assert "graph_nodes.json" in result.stdout
        assert "graph_edges.json" in result.stdout
        assert result.stderr == ""

        nodes = json.loads((output_dir / "graph_nodes.json").read_text(encoding="utf-8"))
        edges = json.loads((output_dir / "graph_edges.json").read_text(encoding="utf-8"))
        assert list(nodes) == ["version", "generated_from", "nodes"]
        assert list(edges) == ["version", "generated_from", "edges"]
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_graph_generation_writes_nothing_for_invalid_bundle() -> None:
    output_dir = _ingest_fixture("invalid-relations-feed", "ms005-cli-invalid")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "graph", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 1
        assert "invalid/raw-only" in result.stderr
        assert not (output_dir / "graph_nodes.json").exists()
        assert not (output_dir / "graph_edges.json").exists()
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_query_behavior_is_unchanged_after_graph_generation() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms005-query-compat")
    try:
        graph_result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "graph", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        query_result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "query", str(output_dir), "routes"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert graph_result.returncode == 0
        assert query_result.returncode == 0
        assert query_result.stderr == ""
        assert json.loads(query_result.stdout) == {
            "routes": [
                {
                    "route": {
                        "route_id": "R1",
                        "agency_id": "A1",
                        "route_short_name": "10",
                        "route_long_name": "Downtown Loop",
                        "route_type": "3",
                        "source_file": "routes.txt",
                        "source_row": 1,
                    },
                    "trip_count": 1,
                }
            ]
        }
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
