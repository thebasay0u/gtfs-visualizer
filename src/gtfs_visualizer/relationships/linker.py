from __future__ import annotations

from dataclasses import dataclass

from gtfs_visualizer.models.normalized import NormalizedFeed


@dataclass(slots=True)
class RelationshipGraph:
    route_to_trip_ids: dict[str, list[str]]
    trip_to_route_id: dict[str, str]
    trip_to_stop_time_keys: dict[str, list[str]]
    stop_time_key_to_stop_id: dict[str, str]
    trip_to_shape_id: dict[str, str]
    service_id_to_calendar_id: dict[str, str]

    def relationship_counts(self) -> dict[str, int]:
        return {
            "route_to_trips": sum(len(trip_ids) for trip_ids in self.route_to_trip_ids.values()),
            "trip_to_stop_times": sum(
                len(stop_time_keys) for stop_time_keys in self.trip_to_stop_time_keys.values()
            ),
            "stop_time_to_stops": len(self.stop_time_key_to_stop_id),
            "trip_to_shapes": len(self.trip_to_shape_id),
            "service_to_calendar": len(self.service_id_to_calendar_id),
        }


def build_relationship_graph(feed: NormalizedFeed) -> RelationshipGraph:
    route_to_trip_ids: dict[str, list[str]] = {
        route_id: [] for route_id in feed.routes
    }
    trip_to_route_id: dict[str, str] = {}
    trip_to_stop_time_keys: dict[str, list[str]] = {
        trip_id: [] for trip_id in feed.trips
    }
    stop_time_key_to_stop_id: dict[str, str] = {}
    trip_to_shape_id: dict[str, str] = {}
    service_id_to_calendar_id: dict[str, str] = {}

    for trip_id, trip in feed.trips.items():
        if trip.route_id in route_to_trip_ids:
            route_to_trip_ids[trip.route_id].append(trip_id)
            trip_to_route_id[trip_id] = trip.route_id
        if trip.shape_id and trip.shape_id in feed.shapes:
            trip_to_shape_id[trip_id] = trip.shape_id
        if trip.service_id in feed.services:
            service_id_to_calendar_id[trip.service_id] = trip.service_id

    for route_id, trip_ids in route_to_trip_ids.items():
        route_to_trip_ids[route_id] = sorted(trip_ids)

    stop_times_by_trip: dict[str, list[tuple[int, str]]] = {}
    for stop_time_key, stop_time in feed.stop_times.items():
        stop_time_key_to_stop_id[stop_time_key] = stop_time.stop_id
        stop_times_by_trip.setdefault(stop_time.trip_id, []).append(
            (stop_time.stop_sequence, stop_time_key)
        )

    for trip_id, ordered_stop_times in stop_times_by_trip.items():
        trip_to_stop_time_keys[trip_id] = [
            stop_time_key
            for _, stop_time_key in sorted(ordered_stop_times, key=lambda item: item[0])
        ]

    return RelationshipGraph(
        route_to_trip_ids=route_to_trip_ids,
        trip_to_route_id=trip_to_route_id,
        trip_to_stop_time_keys=trip_to_stop_time_keys,
        stop_time_key_to_stop_id=stop_time_key_to_stop_id,
        trip_to_shape_id=trip_to_shape_id,
        service_id_to_calendar_id=service_id_to_calendar_id,
    )


def serialize_relationship_graph(
    graph: RelationshipGraph,
    *,
    missing_optional_files: list[str],
) -> dict[str, object]:
    return {
        "missing_optional_files": missing_optional_files,
        "relationship_counts": graph.relationship_counts(),
        "mappings": {
            "route_to_trip_ids": graph.route_to_trip_ids,
            "trip_to_route_id": graph.trip_to_route_id,
            "trip_to_stop_time_keys": graph.trip_to_stop_time_keys,
            "stop_time_key_to_stop_id": graph.stop_time_key_to_stop_id,
            "trip_to_shape_id": graph.trip_to_shape_id,
            "service_id_to_calendar_id": graph.service_id_to_calendar_id,
        },
    }
