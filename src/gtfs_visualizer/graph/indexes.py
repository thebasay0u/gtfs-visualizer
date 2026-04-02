from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from gtfs_visualizer.graph.artifacts import GraphArtifactError, GraphBundle


@dataclass(slots=True)
class GraphIndexBundle:
    node_positions_by_id: dict[str, int]
    node_positions_by_type: dict[str, list[int]]
    edge_positions_by_id: dict[str, int]
    edge_positions_by_type: dict[str, list[int]]
    edge_positions_by_source: dict[str, list[int]]
    edge_positions_by_target: dict[str, list[int]]


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GraphArtifactError(f"Missing required artifact file: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise GraphArtifactError(f"Malformed JSON in artifact file: {path.name}") from exc


def _expected_node_positions_by_id(bundle: GraphBundle) -> dict[str, int]:
    return {
        str(node["id"]): index
        for index, node in enumerate(bundle.nodes)
    }


def _expected_node_positions_by_type(bundle: GraphBundle) -> dict[str, list[int]]:
    positions: dict[str, list[int]] = {}
    for index, node in enumerate(bundle.nodes):
        positions.setdefault(str(node["type"]), []).append(index)
    return {key: positions[key] for key in sorted(positions)}


def _expected_edge_positions_by_id(bundle: GraphBundle) -> dict[str, int]:
    return {
        str(edge["id"]): index
        for index, edge in enumerate(bundle.edges)
    }


def _expected_edge_positions_by_type(bundle: GraphBundle) -> dict[str, list[int]]:
    positions: dict[str, list[int]] = {}
    for index, edge in enumerate(bundle.edges):
        positions.setdefault(str(edge["type"]), []).append(index)
    return {key: positions[key] for key in sorted(positions)}


def _expected_edge_positions_by_source(bundle: GraphBundle) -> dict[str, list[int]]:
    node_ids = [str(node["id"]) for node in bundle.nodes]
    positions = {node_id: [] for node_id in node_ids}
    for index, edge in enumerate(bundle.edges):
        positions[str(edge["source"])].append(index)
    return {key: positions[key] for key in sorted(positions)}


def _expected_edge_positions_by_target(bundle: GraphBundle) -> dict[str, list[int]]:
    node_ids = [str(node["id"]) for node in bundle.nodes]
    positions = {node_id: [] for node_id in node_ids}
    for index, edge in enumerate(bundle.edges):
        positions[str(edge["target"])].append(index)
    return {key: positions[key] for key in sorted(positions)}


def build_graph_index_bundle(bundle: GraphBundle) -> GraphIndexBundle:
    return GraphIndexBundle(
        node_positions_by_id=_expected_node_positions_by_id(bundle),
        node_positions_by_type=_expected_node_positions_by_type(bundle),
        edge_positions_by_id=_expected_edge_positions_by_id(bundle),
        edge_positions_by_type=_expected_edge_positions_by_type(bundle),
        edge_positions_by_source=_expected_edge_positions_by_source(bundle),
        edge_positions_by_target=_expected_edge_positions_by_target(bundle),
    )


def serialize_graph_node_index(
    bundle: GraphBundle,
    index_bundle: GraphIndexBundle,
) -> dict[str, object]:
    return {
        "version": bundle.node_artifact_version,
        "generated_from": {
            "graph_nodes": "graph_nodes.json",
        },
        "node_count": len(bundle.nodes),
        "node_positions_by_id": index_bundle.node_positions_by_id,
        "node_positions_by_type": index_bundle.node_positions_by_type,
    }


def serialize_graph_edge_index(
    bundle: GraphBundle,
    index_bundle: GraphIndexBundle,
) -> dict[str, object]:
    return {
        "version": bundle.edge_artifact_version,
        "generated_from": {
            "graph_nodes": "graph_nodes.json",
            "graph_edges": "graph_edges.json",
        },
        "edge_count": len(bundle.edges),
        "edge_positions_by_id": index_bundle.edge_positions_by_id,
        "edge_positions_by_type": index_bundle.edge_positions_by_type,
        "edge_positions_by_source": index_bundle.edge_positions_by_source,
        "edge_positions_by_target": index_bundle.edge_positions_by_target,
    }


def load_graph_index_bundle(
    artifacts_dir: Path,
    graph_bundle: GraphBundle,
) -> GraphIndexBundle | None:
    node_path = artifacts_dir / "graph_node_index.json"
    edge_path = artifacts_dir / "graph_edge_index.json"
    node_exists = node_path.exists()
    edge_exists = edge_path.exists()

    if not node_exists and not edge_exists:
        return None
    if node_exists != edge_exists:
        raise GraphArtifactError(
            "Graph index artifacts must be present together: graph_node_index.json and "
            "graph_edge_index.json"
        )

    node_data = _load_json(node_path)
    edge_data = _load_json(edge_path)
    if not isinstance(node_data, dict):
        raise GraphArtifactError("Malformed artifact structure: graph_node_index.json must be an object")
    if not isinstance(edge_data, dict):
        raise GraphArtifactError("Malformed artifact structure: graph_edge_index.json must be an object")

    expected = build_graph_index_bundle(graph_bundle)
    expected_node_data = serialize_graph_node_index(graph_bundle, expected)
    expected_edge_data = serialize_graph_edge_index(graph_bundle, expected)

    if node_data != expected_node_data:
        raise GraphArtifactError(
            "Graph index compatibility error: graph_node_index.json does not match "
            "graph_nodes.json"
        )
    if edge_data != expected_edge_data:
        raise GraphArtifactError(
            "Graph index compatibility error: graph_edge_index.json does not match "
            "graph_edges.json"
        )

    return expected
