from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class GraphArtifactError(ValueError):
    """Raised when graph artifacts are missing, malformed, or structurally invalid."""


@dataclass(slots=True)
class GraphBundle:
    node_artifact_version: int
    edge_artifact_version: int
    nodes: list[dict[str, object]]
    edges: list[dict[str, object]]


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GraphArtifactError(f"Missing required artifact file: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise GraphArtifactError(f"Malformed JSON in artifact file: {path.name}") from exc


def _require_mapping(value: object, *, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise GraphArtifactError(f"Malformed artifact structure: {context} must be an object")
    return value


def _require_string(value: object, *, context: str) -> str:
    if not isinstance(value, str):
        raise GraphArtifactError(f"Malformed artifact structure: {context} must be a string")
    return value


def _require_int(value: object, *, context: str) -> int:
    if not isinstance(value, int):
        raise GraphArtifactError(f"Malformed artifact structure: {context} must be an integer")
    return value


def _require_attributes(value: object, *, context: str) -> dict[str, object]:
    return _require_mapping(value, context=context)


def _validate_nodes(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise GraphArtifactError("Malformed artifact structure: graph_nodes.nodes must be an array")

    nodes: list[dict[str, object]] = []
    for index, node in enumerate(value):
        mapping = _require_mapping(node, context=f"graph_nodes.nodes[{index}]")
        _require_string(mapping.get("id"), context=f"graph_nodes.nodes[{index}].id")
        _require_string(mapping.get("type"), context=f"graph_nodes.nodes[{index}].type")
        _require_string(mapping.get("entity_id"), context=f"graph_nodes.nodes[{index}].entity_id")
        _require_string(mapping.get("label"), context=f"graph_nodes.nodes[{index}].label")
        _require_attributes(mapping.get("attributes"), context=f"graph_nodes.nodes[{index}].attributes")
        nodes.append(mapping)
    return nodes


def _validate_edges(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise GraphArtifactError("Malformed artifact structure: graph_edges.edges must be an array")

    edges: list[dict[str, object]] = []
    for index, edge in enumerate(value):
        mapping = _require_mapping(edge, context=f"graph_edges.edges[{index}]")
        _require_string(mapping.get("id"), context=f"graph_edges.edges[{index}].id")
        _require_string(mapping.get("type"), context=f"graph_edges.edges[{index}].type")
        _require_string(mapping.get("source"), context=f"graph_edges.edges[{index}].source")
        _require_string(mapping.get("target"), context=f"graph_edges.edges[{index}].target")
        _require_attributes(mapping.get("attributes"), context=f"graph_edges.edges[{index}].attributes")
        edges.append(mapping)
    return edges


def load_graph_bundle(artifacts_dir: Path) -> GraphBundle:
    nodes_data = _require_mapping(
        _load_json(artifacts_dir / "graph_nodes.json"),
        context="graph_nodes.json",
    )
    edges_data = _require_mapping(
        _load_json(artifacts_dir / "graph_edges.json"),
        context="graph_edges.json",
    )

    node_artifact_version = _require_int(
        nodes_data.get("version"),
        context="graph_nodes.version",
    )
    edge_artifact_version = _require_int(
        edges_data.get("version"),
        context="graph_edges.version",
    )
    nodes = _validate_nodes(nodes_data.get("nodes"))
    edges = _validate_edges(edges_data.get("edges"))
    node_ids = {str(node["id"]) for node in nodes}
    for edge in edges:
        source = str(edge["source"])
        target = str(edge["target"])
        if source not in node_ids or target not in node_ids:
            raise GraphArtifactError(
                f"Invalid graph structure: edge {edge['id']} references missing node"
            )

    return GraphBundle(
        node_artifact_version=node_artifact_version,
        edge_artifact_version=edge_artifact_version,
        nodes=nodes,
        edges=edges,
    )
