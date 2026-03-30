from __future__ import annotations

from dataclasses import dataclass

from gtfs_visualizer.query.artifacts import QueryArtifactError, QueryBundle


class QueryLookupError(LookupError):
    """Raised when a requested route, trip, or stop does not exist."""


@dataclass(slots=True)
class _StopVisit:
    route_id: str
    trip_id: str
    stop_time: dict[str, object]


class QueryService:
    def __init__(self, bundle: QueryBundle) -> None:
        self.bundle = bundle
        self._stop_visits = self._build_stop_visits()

    def list_routes(self) -> dict[str, list[dict[str, object]]]:
        routes: list[dict[str, object]] = []
        for route_id in sorted(self.bundle.routes):
            route = self.bundle.routes[route_id]
            trip_ids = self.bundle.route_to_trip_ids.get(route_id, [])
            routes.append({"route": route, "trip_count": len(trip_ids)})
        return {"routes": routes}

    def get_route_detail(self, route_id: str) -> dict[str, object]:
        route = self._require_route(route_id)
        trip_ids = list(self.bundle.route_to_trip_ids.get(route_id, []))
        return {"route": route, "trip_ids": trip_ids, "trip_count": len(trip_ids)}

    def get_trip_detail(self, trip_id: str) -> dict[str, object]:
        trip = self._require_trip(trip_id)
        route_id = self.bundle.trip_to_route_id.get(trip_id)
        if route_id is None:
            raise QueryArtifactError(f"Malformed artifact structure: trip {trip_id} has no route")
        route = self._require_route(route_id)

        service = None
        service_id = trip.get("service_id")
        if isinstance(service_id, str):
            service_key = self.bundle.service_id_to_calendar_id.get(service_id, service_id)
            service = self.bundle.services.get(service_key)

        shape_points: list[dict[str, object]] = []
        shape_id = self.bundle.trip_to_shape_id.get(trip_id)
        if shape_id is not None:
            shape_points = list(self.bundle.shapes.get(shape_id, []))

        stops: list[dict[str, object]] = []
        for stop_time_key in self.bundle.trip_to_stop_time_keys.get(trip_id, []):
            stop_time = self._require_stop_time(stop_time_key)
            stop_id = self.bundle.stop_time_key_to_stop_id.get(stop_time_key)
            if stop_id is None:
                raise QueryArtifactError(
                    f"Malformed artifact structure: stop_time {stop_time_key} has no stop mapping"
                )
            stop = self._require_stop(stop_id)
            stops.append({"stop_time": stop_time, "stop": stop})

        return {
            "trip": trip,
            "route": route,
            "service": service,
            "shape_points": shape_points,
            "stops": stops,
        }

    def get_stop_detail(self, stop_id: str) -> dict[str, object]:
        stop = self._require_stop(stop_id)
        visits = self._stop_visits.get(stop_id, [])
        route_ids = sorted({visit.route_id for visit in visits})
        trip_ids = sorted({visit.trip_id for visit in visits})
        return {
            "stop": stop,
            "visits": [
                {
                    "route_id": visit.route_id,
                    "trip_id": visit.trip_id,
                    "stop_time": visit.stop_time,
                }
                for visit in visits
            ],
            "route_ids": route_ids,
            "trip_ids": trip_ids,
        }

    def _build_stop_visits(self) -> dict[str, list[_StopVisit]]:
        visits: dict[str, list[_StopVisit]] = {}
        for trip_id, stop_time_keys in self.bundle.trip_to_stop_time_keys.items():
            route_id = self.bundle.trip_to_route_id.get(trip_id)
            if route_id is None:
                raise QueryArtifactError(
                    f"Malformed artifact structure: trip {trip_id} has no route mapping"
                )
            self._require_route(route_id)
            self._require_trip(trip_id)
            for stop_time_key in stop_time_keys:
                stop_time = self._require_stop_time(stop_time_key)
                stop_id = self.bundle.stop_time_key_to_stop_id.get(stop_time_key)
                if stop_id is None:
                    raise QueryArtifactError(
                        f"Malformed artifact structure: stop_time {stop_time_key} has no stop mapping"
                    )
                self._require_stop(stop_id)
                visits.setdefault(stop_id, []).append(
                    _StopVisit(route_id=route_id, trip_id=trip_id, stop_time=stop_time)
                )

        for stop_visits in visits.values():
            stop_visits.sort(
                key=lambda visit: (
                    visit.route_id,
                    visit.trip_id,
                    int(visit.stop_time.get("stop_sequence", 0)),
                )
            )
        return visits

    def _require_route(self, route_id: str) -> dict[str, object]:
        route = self.bundle.routes.get(route_id)
        if route is None:
            raise QueryLookupError(f"Unknown route_id: {route_id}")
        return route

    def _require_trip(self, trip_id: str) -> dict[str, object]:
        trip = self.bundle.trips.get(trip_id)
        if trip is None:
            raise QueryLookupError(f"Unknown trip_id: {trip_id}")
        return trip

    def _require_stop(self, stop_id: str) -> dict[str, object]:
        stop = self.bundle.stops.get(stop_id)
        if stop is None:
            raise QueryLookupError(f"Unknown stop_id: {stop_id}")
        return stop

    def _require_stop_time(self, stop_time_key: str) -> dict[str, object]:
        stop_time = self.bundle.stop_times.get(stop_time_key)
        if stop_time is None:
            raise QueryArtifactError(
                f"Malformed artifact structure: unknown stop_time key {stop_time_key}"
            )
        return stop_time
