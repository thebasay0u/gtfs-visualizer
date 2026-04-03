from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from gtfs_visualizer.graph import (
    GraphArtifactError,
    build_graph_enrichment_artifacts,
    load_graph_bundle,
    load_graph_index_bundle,
    serialize_graph_enrichment_edges,
)

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


def _generate_graph(output_dir: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "gtfs_visualizer.cli", "graph", str(output_dir)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0


def test_graph_enrichment_generation_produces_minimal_route_serves_stop_edges() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms008-minimal")
    try:
        _generate_graph(output_dir)
        bundle = load_graph_bundle(output_dir)
        indexes = load_graph_index_bundle(output_dir, bundle)
        assert indexes is not None

        enrichment = build_graph_enrichment_artifacts(bundle, indexes)
        payload = serialize_graph_enrichment_edges(enrichment)

        assert payload == {
            "version": 1,
            "generated_from": {
                "graph_nodes": "graph_nodes.json",
                "graph_edges": "graph_edges.json",
                "graph_node_index": "graph_node_index.json",
                "graph_edge_index": "graph_edge_index.json",
            },
            "edges": [
                {
                    "id": "route_serves_stop:route:R1:stop:STOP1",
                    "type": "route_serves_stop",
                    "source": "route:R1",
                    "target": "stop:STOP1",
                    "attributes": {"route_id": "R1", "stop_id": "STOP1", "trip_count": 1},
                },
                {
                    "id": "route_serves_stop:route:R1:stop:STOP2",
                    "type": "route_serves_stop",
                    "source": "route:R1",
                    "target": "stop:STOP2",
                    "attributes": {"route_id": "R1", "stop_id": "STOP2", "trip_count": 1},
                },
            ],
        }
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_graph_enrichment_counts_unique_trips_for_shared_and_repeated_stops() -> None:
    output_dir = _ingest_fixture("shared-stop-feed", "ms008-shared-stop")
    try:
        _generate_graph(output_dir)
        bundle = load_graph_bundle(output_dir)
        indexes = load_graph_index_bundle(output_dir, bundle)
        assert indexes is not None

        payload = serialize_graph_enrichment_edges(build_graph_enrichment_artifacts(bundle, indexes))
        assert payload["edges"] == [
            {
                "id": "route_serves_stop:route:R1:stop:STOP1",
                "type": "route_serves_stop",
                "source": "route:R1",
                "target": "stop:STOP1",
                "attributes": {"route_id": "R1", "stop_id": "STOP1", "trip_count": 2},
            },
            {
                "id": "route_serves_stop:route:R1:stop:STOP2",
                "type": "route_serves_stop",
                "source": "route:R1",
                "target": "stop:STOP2",
                "attributes": {"route_id": "R1", "stop_id": "STOP2", "trip_count": 1},
            },
            {
                "id": "route_serves_stop:route:R1:stop:STOP3",
                "type": "route_serves_stop",
                "source": "route:R1",
                "target": "stop:STOP3",
                "attributes": {"route_id": "R1", "stop_id": "STOP3", "trip_count": 1},
            },
        ]
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_graph_enrich_writes_expected_artifact() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms008-cli")
    try:
        _generate_graph(output_dir)
        result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "graph-enrich", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 0
        assert "graph_enrichment_edges.json" in result.stdout
        assert result.stderr == ""
        payload = json.loads((output_dir / "graph_enrichment_edges.json").read_text(encoding="utf-8"))
        assert list(payload) == ["version", "generated_from", "edges"]
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_graph_enrich_fails_when_indexes_are_missing() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms008-missing-index")
    try:
        _generate_graph(output_dir)
        (output_dir / "graph_node_index.json").unlink()
        (output_dir / "graph_edge_index.json").unlink()

        result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "graph-enrich", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 1
        assert result.stdout == ""
        assert "graph index artifacts" in result.stderr
        assert not (output_dir / "graph_enrichment_edges.json").exists()
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_graph_enrich_fails_when_indexes_are_stale() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms008-stale-index")
    try:
        _generate_graph(output_dir)
        edge_index_path = output_dir / "graph_edge_index.json"
        edge_index_payload = json.loads(edge_index_path.read_text(encoding="utf-8"))
        edge_index_payload["version"] = 2
        edge_index_path.write_text(json.dumps(edge_index_payload, indent=2), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "graph-enrich", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 1
        assert result.stdout == ""
        assert "graph_edge_index.json does not match" in result.stderr
        assert not (output_dir / "graph_enrichment_edges.json").exists()
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_graph_enrich_succeeds_for_warning_only_bundle() -> None:
    output_dir = _ingest_fixture("missing-shapes-feed", "ms008-warning")
    try:
        _generate_graph(output_dir)
        result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "graph-enrich", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 0
        payload = json.loads((output_dir / "graph_enrichment_edges.json").read_text(encoding="utf-8"))
        assert [edge["id"] for edge in payload["edges"]] == [
            "route_serves_stop:route:R1:stop:STOP1",
            "route_serves_stop:route:R1:stop:STOP2",
        ]
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
