from __future__ import annotations

from dataclasses import asdict, dataclass

from gtfs_visualizer.graph.artifacts import GraphArtifactError, GraphBundle
from gtfs_visualizer.graph.indexes import GraphIndexBundle


@dataclass(slots=True)
class GraphEnrichmentEdge:
    id: str
    type: str
    source: str
    target: str
    attributes: dict[str, object]


@dataclass(slots=True)
class GraphEnrichmentArtifacts:
    edges: list[GraphEnrichmentEdge]


def build_graph_enrichment_artifacts(
    bundle: GraphBundle,
    indexes: GraphIndexBundle,
) -> GraphEnrichmentArtifacts:
    route_positions = indexes.node_positions_by_type.get("route", [])
    edge_positions_by_source = indexes.edge_positions_by_source
    edge_positions_by_target = indexes.edge_positions_by_target
    route_stop_trip_ids: dict[tuple[str, str], set[str]] = {}

    for route_position in route_positions:
        route_node = bundle.nodes[route_position]
        route_node_id = str(route_node["id"])

        # MS008 Section 7 requires index-driven traversal only, so route expansion starts from
        # precomputed source-edge positions instead of scanning the full graph edge list.
        for route_trip_position in edge_positions_by_source.get(route_node_id, []):
            route_trip_edge = bundle.edges[route_trip_position]
            if route_trip_edge["type"] != "route_has_trip":
                continue

            trip_node_id = str(route_trip_edge["target"])

            # MS008 Sections 3 and 4 require deterministic output and unique trip counting, so
            # repeated visits within one trip accumulate into a set keyed by (route, stop).
            for trip_stop_position in edge_positions_by_source.get(trip_node_id, []):
                trip_stop_edge = bundle.edges[trip_stop_position]
                if trip_stop_edge["type"] != "trip_stops_at":
                    continue

                stop_node_id = str(trip_stop_edge["target"])
                route_stop_trip_ids.setdefault((route_node_id, stop_node_id), set()).add(trip_node_id)

                # MS008 Section 1 requires the enrichment layer to trust validated graph-index
                # prerequisites, so target lookups stay index-based rather than falling back.
                if stop_node_id not in edge_positions_by_target:
                    raise GraphArtifactError(
                        "Graph enrichment compatibility error: graph_edge_index.json is missing "
                        f"target entries for {stop_node_id}"
                    )

    enrichment_edges = [
        GraphEnrichmentEdge(
            # MS008 Section 2 requires IDs to stay canonical and independent of trip_count.
            id=f"route_serves_stop:{source}:{target}",
            type="route_serves_stop",
            source=source,
            target=target,
            attributes={
                "route_id": source.removeprefix("route:"),
                "stop_id": target.removeprefix("stop:"),
                "trip_count": len(trip_ids),
            },
        )
        for (source, target), trip_ids in route_stop_trip_ids.items()
    ]
    enrichment_edges.sort(key=lambda edge: (edge.source, edge.target, edge.type, edge.id))
    return GraphEnrichmentArtifacts(edges=enrichment_edges)


def serialize_graph_enrichment_edges(graph: GraphEnrichmentArtifacts) -> dict[str, object]:
    return {
        "version": 1,
        "generated_from": {
            "graph_nodes": "graph_nodes.json",
            "graph_edges": "graph_edges.json",
            "graph_node_index": "graph_node_index.json",
            "graph_edge_index": "graph_edge_index.json",
        },
        "edges": [asdict(edge) for edge in graph.edges],
    }
