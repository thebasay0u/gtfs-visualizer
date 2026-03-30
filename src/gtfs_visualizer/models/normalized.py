from __future__ import annotations

from dataclasses import asdict, dataclass

from gtfs_visualizer.ingest.feed_loader import RawFeedBundle


@dataclass(slots=True)
class Route:
    route_id: str
    agency_id: str
    route_short_name: str
    route_long_name: str
    route_type: str
    source_file: str
    source_row: int


@dataclass(slots=True)
class Trip:
    trip_id: str
    route_id: str
    service_id: str
    shape_id: str
    source_file: str
    source_row: int


@dataclass(slots=True)
class Stop:
    stop_id: str
    stop_name: str
    stop_lat: str
    stop_lon: str
    source_file: str
    source_row: int


@dataclass(slots=True)
class StopTime:
    stop_time_key: str
    trip_id: str
    arrival_time: str
    departure_time: str
    stop_id: str
    stop_sequence: int
    source_file: str
    source_row: int


@dataclass(slots=True)
class ShapePoint:
    shape_id: str
    shape_pt_lat: str
    shape_pt_lon: str
    shape_pt_sequence: int
    source_file: str
    source_row: int


@dataclass(slots=True)
class ServiceCalendar:
    service_id: str
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str
    start_date: str
    end_date: str
    source_file: str
    source_row: int


@dataclass(slots=True)
class NormalizedFeed:
    routes: dict[str, Route]
    trips: dict[str, Trip]
    stops: dict[str, Stop]
    stop_times: dict[str, StopTime]
    shapes: dict[str, list[ShapePoint]]
    services: dict[str, ServiceCalendar]
    missing_optional_files: list[str]
    raw_row_counts: dict[str, int]

    def entity_counts(self) -> dict[str, int]:
        return {
            "routes": len(self.routes),
            "trips": len(self.trips),
            "stop_times": len(self.stop_times),
            "stops": len(self.stops),
            "services": len(self.services),
            "shapes": len(self.shapes),
        }


def _source_row(index: int) -> int:
    return index + 2


def _serialize_mapping[T](items: dict[str, T]) -> dict[str, dict[str, object]]:
    return {
        key: asdict(value)
        for key, value in items.items()
    }


def normalize_feed(bundle: RawFeedBundle) -> NormalizedFeed:
    routes: dict[str, Route] = {}
    trips: dict[str, Trip] = {}
    stops: dict[str, Stop] = {}
    stop_times: dict[str, StopTime] = {}
    shapes: dict[str, list[ShapePoint]] = {}
    services: dict[str, ServiceCalendar] = {}

    for index, row in bundle.tables["routes"].iterrows():
        route = Route(
            route_id=row["route_id"],
            agency_id=row.get("agency_id", ""),
            route_short_name=row.get("route_short_name", ""),
            route_long_name=row.get("route_long_name", ""),
            route_type=row.get("route_type", ""),
            source_file="routes.txt",
            source_row=_source_row(index),
        )
        routes[route.route_id] = route

    for index, row in bundle.tables["trips"].iterrows():
        trip = Trip(
            trip_id=row["trip_id"],
            route_id=row["route_id"],
            service_id=row["service_id"],
            shape_id=row.get("shape_id", ""),
            source_file="trips.txt",
            source_row=_source_row(index),
        )
        trips[trip.trip_id] = trip

    for index, row in bundle.tables["stops"].iterrows():
        stop = Stop(
            stop_id=row["stop_id"],
            stop_name=row.get("stop_name", ""),
            stop_lat=row.get("stop_lat", ""),
            stop_lon=row.get("stop_lon", ""),
            source_file="stops.txt",
            source_row=_source_row(index),
        )
        stops[stop.stop_id] = stop

    for index, row in bundle.tables["stop_times"].iterrows():
        stop_sequence = int(row["stop_sequence"])
        stop_time = StopTime(
            stop_time_key=f"{row['trip_id']}:{stop_sequence}",
            trip_id=row["trip_id"],
            arrival_time=row.get("arrival_time", ""),
            departure_time=row.get("departure_time", ""),
            stop_id=row["stop_id"],
            stop_sequence=stop_sequence,
            source_file="stop_times.txt",
            source_row=_source_row(index),
        )
        stop_times[stop_time.stop_time_key] = stop_time

    for index, row in bundle.tables["calendar"].iterrows():
        service = ServiceCalendar(
            service_id=row["service_id"],
            monday=row.get("monday", ""),
            tuesday=row.get("tuesday", ""),
            wednesday=row.get("wednesday", ""),
            thursday=row.get("thursday", ""),
            friday=row.get("friday", ""),
            saturday=row.get("saturday", ""),
            sunday=row.get("sunday", ""),
            start_date=row.get("start_date", ""),
            end_date=row.get("end_date", ""),
            source_file="calendar.txt",
            source_row=_source_row(index),
        )
        services[service.service_id] = service

    if "shapes" in bundle.tables:
        for index, row in bundle.tables["shapes"].iterrows():
            shape_point = ShapePoint(
                shape_id=row["shape_id"],
                shape_pt_lat=row.get("shape_pt_lat", ""),
                shape_pt_lon=row.get("shape_pt_lon", ""),
                shape_pt_sequence=int(row["shape_pt_sequence"]),
                source_file="shapes.txt",
                source_row=_source_row(index),
            )
            shapes.setdefault(shape_point.shape_id, []).append(shape_point)

        for shape_id, points in shapes.items():
            points.sort(key=lambda point: point.shape_pt_sequence)

    return NormalizedFeed(
        routes=routes,
        trips=trips,
        stops=stops,
        stop_times=stop_times,
        shapes=shapes,
        services=services,
        missing_optional_files=list(bundle.missing_optional_files),
        raw_row_counts=bundle.row_counts(),
    )


def serialize_normalized_feed(feed: NormalizedFeed) -> dict[str, object]:
    return {
        "entity_counts": feed.entity_counts(),
        "entities": {
            "routes": _serialize_mapping(feed.routes),
            "trips": _serialize_mapping(feed.trips),
            "stops": _serialize_mapping(feed.stops),
            "stop_times": _serialize_mapping(feed.stop_times),
            "shapes": {
                shape_id: [asdict(point) for point in points]
                for shape_id, points in feed.shapes.items()
            },
            "services": _serialize_mapping(feed.services),
        },
    }
