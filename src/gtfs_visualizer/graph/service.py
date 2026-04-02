from __future__ import annotations

from gtfs_visualizer.graph.indexes import GraphIndexBundle
from gtfs_visualizer.graph.artifacts import GraphBundle


class GraphLookupError(LookupError):
    """Raised when a requested graph node or edge does not exist."""


class GraphService:
    def __init__(self, bundle: GraphBundle, indexes: GraphIndexBundle | None = None) -> None:
        self.bundle = bundle
        self.indexes = indexes
        self._nodes_by_id = {str(node["id"]): node for node in bundle.nodes}
        self._edges_by_id = {str(edge["id"]): edge for edge in bundle.edges}
        self._outgoing: dict[str, list[dict[str, object]]] = {}
        self._incoming: dict[str, list[dict[str, object]]] = {}
        for edge in bundle.edges:
            source = str(edge["source"])
            target = str(edge["target"])
            self._outgoing.setdefault(source, []).append(edge)
            self._incoming.setdefault(target, []).append(edge)

    def list_nodes(self, node_type: str | None = None) -> dict[str, object]:
        if node_type is not None and self.indexes is not None:
            positions = self.indexes.node_positions_by_type.get(node_type, [])
            nodes = [self.bundle.nodes[position] for position in positions]
        else:
            nodes = self.bundle.nodes
            if node_type is not None:
                nodes = [node for node in nodes if node["type"] == node_type]
        ordered = sorted(nodes, key=lambda node: (str(node["type"]), str(node["entity_id"])))
        return {"nodes": ordered}

    def get_node(self, node_id: str) -> dict[str, object]:
        return {"node": self._require_node(node_id)}

    def list_edges(
        self,
        edge_type: str | None = None,
        source: str | None = None,
        target: str | None = None,
    ) -> dict[str, object]:
        if self.indexes is not None:
            positions = self._indexed_edge_positions(
                edge_type=edge_type,
                source=source,
                target=target,
            )
            edges = [self.bundle.edges[position] for position in positions]
        else:
            edges = self.bundle.edges
            if edge_type is not None:
                edges = [edge for edge in edges if edge["type"] == edge_type]
            if source is not None:
                edges = [edge for edge in edges if edge["source"] == source]
            if target is not None:
                edges = [edge for edge in edges if edge["target"] == target]
        ordered = sorted(
            edges,
            key=lambda edge: (
                str(edge["type"]),
                str(edge["source"]),
                str(edge["target"]),
                int(edge["attributes"].get("stop_sequence", -1)),
                str(edge["id"]),
            ),
        )
        return {"edges": ordered}

    def get_edge(self, edge_id: str) -> dict[str, object]:
        return {"edge": self._require_edge(edge_id)}

    def get_neighbors(
        self,
        node_id: str,
        direction: str = "both",
        edge_type: str | None = None,
    ) -> dict[str, object]:
        node = self._require_node(node_id)
        edges = self._filtered_edges(node_id=node_id, direction=direction, edge_type=edge_type)
        neighbor_map: dict[str, dict[str, object]] = {}
        for edge in edges:
            source = str(edge["source"])
            target = str(edge["target"])
            if direction == "out":
                neighbor_id = target
            elif direction == "in":
                neighbor_id = source
            else:
                neighbor_id = target if source == node_id else source
            neighbor_map.setdefault(neighbor_id, self._require_node(neighbor_id))

        neighbors = sorted(
            neighbor_map.values(),
            key=lambda item: (str(item["type"]), str(item["entity_id"])),
        )
        return {"node": node, "neighbors": neighbors, "edges": edges}

    def _filtered_edges(
        self,
        *,
        node_id: str,
        direction: str,
        edge_type: str | None,
    ) -> list[dict[str, object]]:
        if self.indexes is not None:
            if direction == "out":
                positions = self.indexes.edge_positions_by_source.get(node_id, [])
            elif direction == "in":
                positions = self.indexes.edge_positions_by_target.get(node_id, [])
            else:
                positions = (
                    self.indexes.edge_positions_by_source.get(node_id, [])
                    + self.indexes.edge_positions_by_target.get(node_id, [])
                )
            candidates = [self.bundle.edges[position] for position in positions]
        else:
            if direction == "out":
                candidates = list(self._outgoing.get(node_id, []))
            elif direction == "in":
                candidates = list(self._incoming.get(node_id, []))
            else:
                candidates = list(self._outgoing.get(node_id, [])) + list(self._incoming.get(node_id, []))

        if edge_type is not None:
            candidates = [edge for edge in candidates if edge["type"] == edge_type]

        return sorted(
            candidates,
            key=lambda edge: (
                str(edge["type"]),
                str(edge["source"]),
                str(edge["target"]),
                int(edge["attributes"].get("stop_sequence", -1)),
                str(edge["id"]),
            ),
        )

    def _indexed_edge_positions(
        self,
        *,
        edge_type: str | None,
        source: str | None,
        target: str | None,
    ) -> list[int]:
        assert self.indexes is not None
        positions: set[int] | None = None

        if edge_type is not None:
            positions = set(self.indexes.edge_positions_by_type.get(edge_type, []))
        if source is not None:
            source_positions = set(self.indexes.edge_positions_by_source.get(source, []))
            positions = source_positions if positions is None else positions & source_positions
        if target is not None:
            target_positions = set(self.indexes.edge_positions_by_target.get(target, []))
            positions = target_positions if positions is None else positions & target_positions
        if positions is None:
            positions = set(range(len(self.bundle.edges)))

        return sorted(positions)

    def _require_node(self, node_id: str) -> dict[str, object]:
        node = self._nodes_by_id.get(node_id)
        if node is None:
            raise GraphLookupError(f"Unknown node_id: {node_id}")
        return node

    def _require_edge(self, edge_id: str) -> dict[str, object]:
        edge = self._edges_by_id.get(edge_id)
        if edge is None:
            raise GraphLookupError(f"Unknown edge_id: {edge_id}")
        return edge
