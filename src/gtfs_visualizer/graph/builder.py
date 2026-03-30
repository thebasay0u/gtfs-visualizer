from __future__ import annotations

from dataclasses import asdict, dataclass

from gtfs_visualizer.artifacts import ValidatedArtifactBundle


@dataclass(slots=True)
class GraphNode:
    id: str
    type: str
    entity_id: str
    label: str
    attributes: dict[str, object]


@dataclass(slots=True)
class GraphEdge:
    id: str
    type: str
    source: str
    target: str
    attributes: dict[str, object]


@dataclass(slots=True)
class GraphArtifacts:
    nodes: list[GraphNode]
    edges: list[GraphEdge]


def _compact_attributes(attributes: dict[str, object]) -> dict[str, object]:
    compact: dict[str, object] = {}
    for key, value in attributes.items():
        if value is None:
            continue
        if isinstance(value, str) and value == "":
            continue
        if isinstance(value, list) and not value:
            continue
        if isinstance(value, dict) and not value:
            continue
        compact[key] = value
    return compact


def _parse_int(value: object) -> object:
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return value


def _route_label(route: dict[str, object]) -> str:
    route_short_name = route.get("route_short_name")
    route_long_name = route.get("route_long_name")
    if isinstance(route_short_name, str) and route_short_name:
        return f"Route {route_short_name}"
    if isinstance(route_long_name, str) and route_long_name:
        return route_long_name
    return str(route.get("route_id", ""))


def _trip_label(trip: dict[str, object]) -> str:
    return f"Trip {trip['trip_id']}"


def _stop_label(stop: dict[str, object]) -> str:
    stop_name = stop.get("stop_name")
    if isinstance(stop_name, str) and stop_name:
        return stop_name
    return str(stop.get("stop_id", ""))


def _route_node(route_id: str, route: dict[str, object]) -> GraphNode:
    return GraphNode(
        id=f"route:{route_id}",
        type="route",
        entity_id=route_id,
        label=_route_label(route),
        attributes=_compact_attributes(
            {
                "route_id": route.get("route_id"),
                "route_short_name": route.get("route_short_name"),
                "route_long_name": route.get("route_long_name"),
                "route_type": _parse_int(route.get("route_type")),
            }
        ),
    )


def _trip_node(trip_id: str, trip: dict[str, object]) -> GraphNode:
    return GraphNode(
        id=f"trip:{trip_id}",
        type="trip",
        entity_id=trip_id,
        label=_trip_label(trip),
        attributes=_compact_attributes(
            {
                "trip_id": trip.get("trip_id"),
                "route_id": trip.get("route_id"),
                "service_id": trip.get("service_id"),
                "shape_id": trip.get("shape_id"),
            }
        ),
    )


def _stop_node(stop_id: str, stop: dict[str, object]) -> GraphNode:
    return GraphNode(
        id=f"stop:{stop_id}",
        type="stop",
        entity_id=stop_id,
        label=_stop_label(stop),
        attributes=_compact_attributes(
            {
                "stop_id": stop.get("stop_id"),
                "stop_name": stop.get("stop_name"),
                "stop_lat": stop.get("stop_lat"),
                "stop_lon": stop.get("stop_lon"),
            }
        ),
    )


def build_graph_artifacts(bundle: ValidatedArtifactBundle) -> GraphArtifacts:
    nodes: list[GraphNode] = []
    for route_id, route in bundle.routes.items():
        nodes.append(_route_node(route_id, route))
    for stop_id, stop in bundle.stops.items():
        nodes.append(_stop_node(stop_id, stop))
    for trip_id, trip in bundle.trips.items():
        nodes.append(_trip_node(trip_id, trip))

    nodes.sort(key=lambda node: (node.type, node.entity_id))

    edges: list[GraphEdge] = []
    seen_route_trip: set[tuple[str, str]] = set()
    for route_id, trip_ids in bundle.route_to_trip_ids.items():
        for trip_id in trip_ids:
            edge_key = (route_id, trip_id)
            if edge_key in seen_route_trip:
                continue
            seen_route_trip.add(edge_key)
            edges.append(
                GraphEdge(
                    id=f"route_has_trip:route:{route_id}:trip:{trip_id}",
                    type="route_has_trip",
                    source=f"route:{route_id}",
                    target=f"trip:{trip_id}",
                    attributes={"route_id": route_id, "trip_id": trip_id},
                )
            )

    seen_trip_stop: set[tuple[str, str, int]] = set()
    for trip_id, stop_time_keys in bundle.trip_to_stop_time_keys.items():
        for stop_time_key in stop_time_keys:
            stop_time = bundle.stop_times[stop_time_key]
            stop_id = bundle.stop_time_key_to_stop_id[stop_time_key]
            stop_sequence = int(stop_time["stop_sequence"])
            edge_key = (trip_id, stop_id, stop_sequence)
            if edge_key in seen_trip_stop:
                continue
            seen_trip_stop.add(edge_key)
            edges.append(
                GraphEdge(
                    id=f"trip_stops_at:trip:{trip_id}:stop:{stop_id}:{stop_sequence}",
                    type="trip_stops_at",
                    source=f"trip:{trip_id}",
                    target=f"stop:{stop_id}",
                    attributes=_compact_attributes(
                        {
                            "trip_id": trip_id,
                            "stop_id": stop_id,
                            "stop_sequence": stop_sequence,
                        }
                    ),
                )
            )

    edges.sort(
        key=lambda edge: (
            edge.type,
            edge.source,
            edge.target,
            int(edge.attributes.get("stop_sequence", -1)),
        )
    )
    return GraphArtifacts(nodes=nodes, edges=edges)


def serialize_graph_nodes(graph: GraphArtifacts) -> dict[str, object]:
    return {
        "version": 1,
        "generated_from": {
            "normalized_entities": "normalized_entities.json",
            "relationships": "relationships.json",
        },
        "nodes": [asdict(node) for node in graph.nodes],
    }


def serialize_graph_edges(graph: GraphArtifacts) -> dict[str, object]:
    return {
        "version": 1,
        "generated_from": {
            "normalized_entities": "normalized_entities.json",
            "relationships": "relationships.json",
        },
        "edges": [asdict(edge) for edge in graph.edges],
    }
