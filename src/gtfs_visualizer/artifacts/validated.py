from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class ArtifactBundleError(ValueError):
    """Raised when validated artifacts are missing, invalid, or malformed."""


@dataclass(slots=True)
class ValidatedArtifactBundle:
    routes: dict[str, dict[str, object]]
    trips: dict[str, dict[str, object]]
    stops: dict[str, dict[str, object]]
    stop_times: dict[str, dict[str, object]]
    shapes: dict[str, list[dict[str, object]]]
    services: dict[str, dict[str, object]]
    route_to_trip_ids: dict[str, list[str]]
    trip_to_route_id: dict[str, str]
    trip_to_stop_time_keys: dict[str, list[str]]
    stop_time_key_to_stop_id: dict[str, str]
    trip_to_shape_id: dict[str, str]
    service_id_to_calendar_id: dict[str, str]


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ArtifactBundleError(f"Missing required artifact file: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise ArtifactBundleError(f"Malformed JSON in artifact file: {path.name}") from exc


def _require_mapping(value: object, *, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ArtifactBundleError(f"Malformed artifact structure: {context} must be an object")
    return value


def _require_string(value: object, *, context: str) -> str:
    if not isinstance(value, str):
        raise ArtifactBundleError(f"Malformed artifact structure: {context} must be a string")
    return value


def _require_entity_mapping(value: object, *, context: str) -> dict[str, dict[str, object]]:
    mapping = _require_mapping(value, context=context)
    for key, item in mapping.items():
        if not isinstance(key, str) or not isinstance(item, dict):
            raise ArtifactBundleError(
                f"Malformed artifact structure: {context} must map strings to objects"
            )
    return mapping


def _require_shapes_mapping(
    value: object, *, context: str
) -> dict[str, list[dict[str, object]]]:
    mapping = _require_mapping(value, context=context)
    normalized: dict[str, list[dict[str, object]]] = {}
    for key, item in mapping.items():
        if not isinstance(key, str) or not isinstance(item, list):
            raise ArtifactBundleError(
                f"Malformed artifact structure: {context} must map strings to arrays"
            )
        points: list[dict[str, object]] = []
        for point in item:
            if not isinstance(point, dict):
                raise ArtifactBundleError(
                    f"Malformed artifact structure: {context} entries must be objects"
                )
            points.append(point)
        normalized[key] = points
    return normalized


def _require_string_list_mapping(value: object, *, context: str) -> dict[str, list[str]]:
    mapping = _require_mapping(value, context=context)
    normalized: dict[str, list[str]] = {}
    for key, item in mapping.items():
        if not isinstance(key, str) or not isinstance(item, list):
            raise ArtifactBundleError(
                f"Malformed artifact structure: {context} must map strings to arrays"
            )
        values: list[str] = []
        for index, entry in enumerate(item):
            values.append(_require_string(entry, context=f"{context}.{key}[{index}]"))
        normalized[key] = values
    return normalized


def _require_string_mapping(value: object, *, context: str) -> dict[str, str]:
    mapping = _require_mapping(value, context=context)
    normalized: dict[str, str] = {}
    for key, item in mapping.items():
        if not isinstance(key, str):
            raise ArtifactBundleError(
                f"Malformed artifact structure: {context} keys must be strings"
            )
        normalized[key] = _require_string(item, context=f"{context}.{key}")
    return normalized


def load_validated_artifact_bundle(artifacts_dir: Path) -> ValidatedArtifactBundle:
    validation_data = _require_mapping(
        _load_json(artifacts_dir / "validation_report.json"),
        context="validation_report.json",
    )
    status = _require_string(validation_data.get("status"), context="validation_report.status")
    partial_ingestion = _require_mapping(
        validation_data.get("partial_ingestion"),
        context="validation_report.partial_ingestion",
    )
    partial_state = _require_string(
        partial_ingestion.get("state"),
        context="validation_report.partial_ingestion.state",
    )
    if status == "invalid" or partial_state == "raw_only":
        raise ArtifactBundleError("Artifacts are unavailable for invalid/raw-only bundles")

    normalized_data = _require_mapping(
        _load_json(artifacts_dir / "normalized_entities.json"),
        context="normalized_entities.json",
    )
    entities = _require_mapping(
        normalized_data.get("entities"),
        context="normalized_entities.entities",
    )

    relationships_data = _require_mapping(
        _load_json(artifacts_dir / "relationships.json"),
        context="relationships.json",
    )
    mappings = _require_mapping(
        relationships_data.get("mappings"),
        context="relationships.mappings",
    )

    return ValidatedArtifactBundle(
        routes=_require_entity_mapping(entities.get("routes"), context="entities.routes"),
        trips=_require_entity_mapping(entities.get("trips"), context="entities.trips"),
        stops=_require_entity_mapping(entities.get("stops"), context="entities.stops"),
        stop_times=_require_entity_mapping(
            entities.get("stop_times"),
            context="entities.stop_times",
        ),
        shapes=_require_shapes_mapping(entities.get("shapes"), context="entities.shapes"),
        services=_require_entity_mapping(entities.get("services"), context="entities.services"),
        route_to_trip_ids=_require_string_list_mapping(
            mappings.get("route_to_trip_ids"),
            context="mappings.route_to_trip_ids",
        ),
        trip_to_route_id=_require_string_mapping(
            mappings.get("trip_to_route_id"),
            context="mappings.trip_to_route_id",
        ),
        trip_to_stop_time_keys=_require_string_list_mapping(
            mappings.get("trip_to_stop_time_keys"),
            context="mappings.trip_to_stop_time_keys",
        ),
        stop_time_key_to_stop_id=_require_string_mapping(
            mappings.get("stop_time_key_to_stop_id"),
            context="mappings.stop_time_key_to_stop_id",
        ),
        trip_to_shape_id=_require_string_mapping(
            mappings.get("trip_to_shape_id"),
            context="mappings.trip_to_shape_id",
        ),
        service_id_to_calendar_id=_require_string_mapping(
            mappings.get("service_id_to_calendar_id"),
            context="mappings.service_id_to_calendar_id",
        ),
    )
