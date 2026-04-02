from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from gtfs_visualizer.graph import (
    GraphArtifactError,
    GraphLookupError,
    GraphService,
    load_graph_bundle,
    load_graph_index_bundle,
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


def test_load_graph_bundle_accepts_valid_and_warning_only_graph_artifacts() -> None:
    valid_dir = _ingest_fixture("minimal-static-feed", "ms006-valid")
    warning_dir = _ingest_fixture("missing-shapes-feed", "ms006-warning")
    try:
        _generate_graph(valid_dir)
        _generate_graph(warning_dir)

        valid_bundle = load_graph_bundle(valid_dir)
        warning_bundle = load_graph_bundle(warning_dir)

        assert len(valid_bundle.nodes) == 4
        assert len(valid_bundle.edges) == 3
        assert len(warning_bundle.nodes) == 4
        assert len(warning_bundle.edges) == 3
    finally:
        shutil.rmtree(valid_dir, ignore_errors=True)
        shutil.rmtree(warning_dir, ignore_errors=True)


def test_load_graph_bundle_rejects_missing_graph_artifacts_without_recovery() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms006-missing-graph")
    try:
        try:
            load_graph_bundle(output_dir)
        except GraphArtifactError as exc:
            assert "graph_nodes.json" in str(exc)
        else:
            raise AssertionError("Expected GraphArtifactError")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_load_graph_bundle_rejects_invalid_edge_references() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms006-invalid-edge")
    try:
        _generate_graph(output_dir)
        edges_path = output_dir / "graph_edges.json"
        edges_payload = json.loads(edges_path.read_text(encoding="utf-8"))
        edges_payload["edges"][0]["target"] = "trip:T_UNKNOWN"
        edges_path.write_text(json.dumps(edges_payload, indent=2), encoding="utf-8")

        try:
            load_graph_bundle(output_dir)
        except GraphArtifactError as exc:
            assert "references missing node" in str(exc)
        else:
            raise AssertionError("Expected GraphArtifactError")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_graph_service_supports_deterministic_reads_and_deduplicated_neighbors() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms006-service")
    try:
        _generate_graph(output_dir)
        graph_bundle = load_graph_bundle(output_dir)
        service = GraphService(graph_bundle, indexes=load_graph_index_bundle(output_dir, graph_bundle))

        nodes = service.list_nodes()
        edges = service.list_edges()
        node = service.get_node("trip:T1")
        edge = service.get_edge("route_has_trip:route:R1:trip:T1")
        neighbors = service.get_neighbors("trip:T1", direction="both")

        assert [item["id"] for item in nodes["nodes"]] == [
            "route:R1",
            "stop:STOP1",
            "stop:STOP2",
            "trip:T1",
        ]
        assert [item["id"] for item in edges["edges"]] == [
            "route_has_trip:route:R1:trip:T1",
            "trip_stops_at:trip:T1:stop:STOP1:1",
            "trip_stops_at:trip:T1:stop:STOP2:2",
        ]
        assert node["node"]["id"] == "trip:T1"
        assert edge["edge"]["id"] == "route_has_trip:route:R1:trip:T1"
        assert [item["id"] for item in neighbors["neighbors"]] == [
            "route:R1",
            "stop:STOP1",
            "stop:STOP2",
        ]
        assert [item["id"] for item in neighbors["edges"]] == [
            "route_has_trip:route:R1:trip:T1",
            "trip_stops_at:trip:T1:stop:STOP1:1",
            "trip_stops_at:trip:T1:stop:STOP2:2",
        ]
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_graph_service_supports_filtered_edges_and_neighbors() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms006-filters")
    try:
        _generate_graph(output_dir)
        graph_bundle = load_graph_bundle(output_dir)
        service = GraphService(graph_bundle, indexes=load_graph_index_bundle(output_dir, graph_bundle))

        route_edges = service.list_edges(edge_type="route_has_trip", source="route:R1")
        out_neighbors = service.get_neighbors("trip:T1", direction="out", edge_type="trip_stops_at")
        in_neighbors = service.get_neighbors("trip:T1", direction="in", edge_type="route_has_trip")

        assert [item["id"] for item in route_edges["edges"]] == ["route_has_trip:route:R1:trip:T1"]
        assert [item["id"] for item in out_neighbors["neighbors"]] == ["stop:STOP1", "stop:STOP2"]
        assert [item["id"] for item in out_neighbors["edges"]] == [
            "trip_stops_at:trip:T1:stop:STOP1:1",
            "trip_stops_at:trip:T1:stop:STOP2:2",
        ]
        assert [item["id"] for item in in_neighbors["neighbors"]] == ["route:R1"]
        assert [item["id"] for item in in_neighbors["edges"]] == ["route_has_trip:route:R1:trip:T1"]
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_graph_service_raises_lookup_error_only_for_unknown_node_and_edge_ids() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms006-lookup")
    try:
        _generate_graph(output_dir)
        graph_bundle = load_graph_bundle(output_dir)
        service = GraphService(graph_bundle, indexes=load_graph_index_bundle(output_dir, graph_bundle))

        try:
            service.get_node("trip:T_UNKNOWN")
        except GraphLookupError as exc:
            assert "Unknown node_id" in str(exc)
        else:
            raise AssertionError("Expected GraphLookupError for node")

        try:
            service.get_edge("trip_stops_at:unknown")
        except GraphLookupError as exc:
            assert "Unknown edge_id" in str(exc)
        else:
            raise AssertionError("Expected GraphLookupError for edge")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_graph_read_commands_emit_deterministic_shapes() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms006-cli")
    try:
        _generate_graph(output_dir)
        expectations = [
            (["nodes"], ["nodes"]),
            (["node", "trip:T1"], ["node"]),
            (["edges", "--type", "trip_stops_at"], ["edges"]),
            (["edge", "route_has_trip:route:R1:trip:T1"], ["edge"]),
            (["neighbors", "trip:T1", "--direction", "out"], ["node", "neighbors", "edges"]),
        ]
        for args, expected_keys in expectations:
            result = subprocess.run(
                [sys.executable, "-m", "gtfs_visualizer.cli", "graph-read", str(output_dir), *args],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                check=False,
            )
            assert result.returncode == 0
            assert result.stderr == ""
            payload = json.loads(result.stdout)
            assert list(payload) == expected_keys
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_graph_read_failures_print_to_stderr_and_do_not_generate_artifacts() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms006-cli-failure")
    lookup_dir = _ingest_fixture("minimal-static-feed", "ms006-cli-lookup")
    try:
        missing_result = subprocess.run(
            [sys.executable, "-m", "gtfs_visualizer.cli", "graph-read", str(output_dir), "nodes"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        assert not (output_dir / "graph_nodes.json").exists()
        assert not (output_dir / "graph_edges.json").exists()

        _generate_graph(lookup_dir)
        lookup_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "gtfs_visualizer.cli",
                "graph-read",
                str(lookup_dir),
                "node",
                "trip:T_UNKNOWN",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert missing_result.returncode == 1
        assert missing_result.stdout == ""
        assert "graph_nodes.json" in missing_result.stderr
        assert not (output_dir / "graph_nodes.json").exists()
        assert not (output_dir / "graph_edges.json").exists()
        assert not (output_dir / "graph_node_index.json").exists()
        assert not (output_dir / "graph_edge_index.json").exists()

        assert lookup_result.returncode == 1
        assert lookup_result.stdout == ""
        assert "Unknown node_id" in lookup_result.stderr
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
        shutil.rmtree(lookup_dir, ignore_errors=True)


def test_graph_read_outputs_match_exactly_with_and_without_indexes() -> None:
    indexed_dir = _ingest_fixture("minimal-static-feed", "ms007-indexed")
    fallback_dir = _ingest_fixture("minimal-static-feed", "ms007-fallback")
    try:
        _generate_graph(indexed_dir)
        _generate_graph(fallback_dir)
        (fallback_dir / "graph_node_index.json").unlink()
        (fallback_dir / "graph_edge_index.json").unlink()

        commands = [
            ["nodes"],
            ["node", "trip:T1"],
            ["edges", "--type", "trip_stops_at"],
            ["edge", "route_has_trip:route:R1:trip:T1"],
            ["neighbors", "trip:T1", "--direction", "both"],
        ]
        for args in commands:
            indexed_result = subprocess.run(
                [sys.executable, "-m", "gtfs_visualizer.cli", "graph-read", str(indexed_dir), *args],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                check=False,
            )
            fallback_result = subprocess.run(
                [sys.executable, "-m", "gtfs_visualizer.cli", "graph-read", str(fallback_dir), *args],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                check=False,
            )

            assert indexed_result.returncode == 0
            assert fallback_result.returncode == 0
            assert indexed_result.stdout == fallback_result.stdout
            assert indexed_result.stderr == fallback_result.stderr == ""
    finally:
        shutil.rmtree(indexed_dir, ignore_errors=True)
        shutil.rmtree(fallback_dir, ignore_errors=True)


def test_load_graph_index_bundle_rejects_partial_index_presence() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms007-partial-index")
    try:
        _generate_graph(output_dir)
        (output_dir / "graph_edge_index.json").unlink()

        try:
            load_graph_index_bundle(output_dir, load_graph_bundle(output_dir))
        except GraphArtifactError as exc:
            assert "must be present together" in str(exc)
        else:
            raise AssertionError("Expected GraphArtifactError")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_load_graph_index_bundle_rejects_mismatched_index_artifacts() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms007-mismatched-index")
    try:
        _generate_graph(output_dir)
        node_index_path = output_dir / "graph_node_index.json"
        node_index_payload = json.loads(node_index_path.read_text(encoding="utf-8"))
        node_index_payload["node_positions_by_id"]["trip:T_EXTRA"] = 3
        node_index_path.write_text(json.dumps(node_index_payload, indent=2), encoding="utf-8")

        try:
            load_graph_index_bundle(output_dir, load_graph_bundle(output_dir))
        except GraphArtifactError as exc:
            assert "graph_node_index.json does not match" in str(exc)
        else:
            raise AssertionError("Expected GraphArtifactError")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_load_graph_index_bundle_rejects_missing_index_ids() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms007-missing-index-id")
    try:
        _generate_graph(output_dir)
        edge_index_path = output_dir / "graph_edge_index.json"
        edge_index_payload = json.loads(edge_index_path.read_text(encoding="utf-8"))
        edge_index_payload["edge_positions_by_id"].pop("trip_stops_at:trip:T1:stop:STOP2:2")
        edge_index_path.write_text(json.dumps(edge_index_payload, indent=2), encoding="utf-8")

        try:
            load_graph_index_bundle(output_dir, load_graph_bundle(output_dir))
        except GraphArtifactError as exc:
            assert "graph_edge_index.json does not match" in str(exc)
        else:
            raise AssertionError("Expected GraphArtifactError")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_load_graph_index_bundle_rejects_stale_version_linkage() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms007-stale-version")
    try:
        _generate_graph(output_dir)
        edge_index_path = output_dir / "graph_edge_index.json"
        edge_index_payload = json.loads(edge_index_path.read_text(encoding="utf-8"))
        edge_index_payload["version"] = 2
        edge_index_path.write_text(json.dumps(edge_index_payload, indent=2), encoding="utf-8")

        try:
            load_graph_index_bundle(output_dir, load_graph_bundle(output_dir))
        except GraphArtifactError as exc:
            assert "graph_edge_index.json does not match" in str(exc)
        else:
            raise AssertionError("Expected GraphArtifactError")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
