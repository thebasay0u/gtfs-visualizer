from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import pandas as pd

from gtfs_visualizer.ingest.feed_loader import OPTIONAL_GTFS_FILES, RawFeedBundle
from gtfs_visualizer.models.normalized import NormalizedFeed
from gtfs_visualizer.relationships.linker import RelationshipGraph

ValidationStatus = Literal["valid", "valid_with_warnings", "invalid"]
ValidationSeverity = Literal["warning", "error"]
ValidationFindingCode = Literal[
    "DUPLICATE_ROUTE_ID",
    "DUPLICATE_TRIP_ID",
    "DUPLICATE_STOP_ID",
    "DUPLICATE_SERVICE_ID",
    "DUPLICATE_STOP_TIME_KEY",
    "UNKNOWN_ROUTE_ID",
    "UNKNOWN_TRIP_ID",
    "UNKNOWN_STOP_ID",
    "UNKNOWN_SERVICE_ID",
    "MISSING_OPTIONAL_SHAPES_FILE",
    "MISSING_OPTIONAL_CALENDAR_DATES_FILE",
    "UNKNOWN_SHAPE_ID",
    "SHAPE_ID_WITHOUT_SHAPES_FILE",
]
EntityType = Literal["feed", "route", "trip", "stop", "stop_time", "shape", "service"]


@dataclass(slots=True)
class ValidationIssue:
    severity: ValidationSeverity
    code: ValidationFindingCode
    message: str
    entity_type: EntityType
    entity_id: str
    source_file: str
    source_row: int
    related: dict[str, str]


@dataclass(slots=True)
class ValidationReport:
    status: ValidationStatus
    findings: list[ValidationIssue]
    missing_optional_files: list[str]
    written_artifacts: list[str]
    suppressed_artifacts: list[str]

    def error_count(self) -> int:
        return sum(issue.severity == "error" for issue in self.findings)

    def warning_count(self) -> int:
        return sum(issue.severity == "warning" for issue in self.findings)


def _add_issue(
    findings: list[ValidationIssue],
    *,
    severity: ValidationSeverity,
    code: ValidationFindingCode,
    message: str,
    entity_type: EntityType,
    entity_id: str,
    source_file: str,
    source_row: int,
    related: dict[str, str] | None = None,
) -> None:
    findings.append(
        ValidationIssue(
            severity=severity,
            code=code,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            source_file=source_file,
            source_row=source_row,
            related=related or {},
        )
    )


def _find_duplicates(
    table: pd.DataFrame,
    key_field: str,
    *,
    code: ValidationFindingCode,
    entity_type: EntityType,
    source_file: str,
) -> list[ValidationIssue]:
    findings: list[ValidationIssue] = []
    seen: set[str] = set()
    for index, row in table.iterrows():
        value = row[key_field]
        if value in seen:
            _add_issue(
                findings,
                severity="error",
                code=code,
                message=f"{source_file} contains duplicate {key_field} {value}",
                entity_type=entity_type,
                entity_id=value,
                source_file=source_file,
                source_row=index + 1,
                related={"field": key_field, "value": value},
            )
        else:
            seen.add(value)
    return findings


def _find_duplicate_stop_time_keys(table: pd.DataFrame) -> list[ValidationIssue]:
    findings: list[ValidationIssue] = []
    seen: set[str] = set()
    for index, row in table.iterrows():
        key = f"{row['trip_id']}:{row['stop_sequence']}"
        if key in seen:
            _add_issue(
                findings,
                severity="error",
                code="DUPLICATE_STOP_TIME_KEY",
                message=f"stop_times.txt contains duplicate stop_time key {key}",
                entity_type="stop_time",
                entity_id=key,
                source_file="stop_times.txt",
                source_row=index + 1,
                related={"field": "trip_id:stop_sequence", "value": key},
            )
        else:
            seen.add(key)
    return findings


def validate_feed(
    bundle: RawFeedBundle,
    feed: NormalizedFeed,
    graph: RelationshipGraph,
) -> ValidationReport:
    findings: list[ValidationIssue] = []

    findings.extend(
        _find_duplicates(
            bundle.tables["routes"],
            "route_id",
            code="DUPLICATE_ROUTE_ID",
            entity_type="route",
            source_file="routes.txt",
        )
    )
    findings.extend(
        _find_duplicates(
            bundle.tables["trips"],
            "trip_id",
            code="DUPLICATE_TRIP_ID",
            entity_type="trip",
            source_file="trips.txt",
        )
    )
    findings.extend(
        _find_duplicates(
            bundle.tables["stops"],
            "stop_id",
            code="DUPLICATE_STOP_ID",
            entity_type="stop",
            source_file="stops.txt",
        )
    )
    findings.extend(
        _find_duplicates(
            bundle.tables["calendar"],
            "service_id",
            code="DUPLICATE_SERVICE_ID",
            entity_type="service",
            source_file="calendar.txt",
        )
    )
    findings.extend(_find_duplicate_stop_time_keys(bundle.tables["stop_times"]))

    for optional_file in OPTIONAL_GTFS_FILES:
        if optional_file not in bundle.loaded_files:
            if optional_file == "shapes.txt":
                _add_issue(
                    findings,
                    severity="warning",
                    code="MISSING_OPTIONAL_SHAPES_FILE",
                    message="Optional GTFS file shapes.txt is missing",
                    entity_type="feed",
                    entity_id="",
                    source_file="shapes.txt",
                    source_row=0,
                )
            elif optional_file == "calendar_dates.txt":
                _add_issue(
                    findings,
                    severity="warning",
                    code="MISSING_OPTIONAL_CALENDAR_DATES_FILE",
                    message="Optional GTFS file calendar_dates.txt is missing",
                    entity_type="feed",
                    entity_id="",
                    source_file="calendar_dates.txt",
                    source_row=0,
                )

    for trip in feed.trips.values():
        if trip.trip_id not in graph.trip_to_route_id:
            _add_issue(
                findings,
                severity="error",
                code="UNKNOWN_ROUTE_ID",
                message=f"Trip {trip.trip_id} references unknown route_id {trip.route_id}",
                entity_type="trip",
                entity_id=trip.trip_id,
                source_file=trip.source_file,
                source_row=trip.source_row,
                related={"field": "route_id", "value": trip.route_id},
            )

        if trip.service_id not in graph.service_id_to_calendar_id:
            _add_issue(
                findings,
                severity="error",
                code="UNKNOWN_SERVICE_ID",
                message=f"Trip {trip.trip_id} references unknown service_id {trip.service_id}",
                entity_type="trip",
                entity_id=trip.trip_id,
                source_file=trip.source_file,
                source_row=trip.source_row,
                related={"field": "service_id", "value": trip.service_id},
            )

        if trip.shape_id:
            if "shapes.txt" not in bundle.loaded_files:
                _add_issue(
                    findings,
                    severity="warning",
                    code="SHAPE_ID_WITHOUT_SHAPES_FILE",
                    message=(
                        f"Trip {trip.trip_id} declares shape_id {trip.shape_id} but shapes.txt "
                        "is missing"
                    ),
                    entity_type="trip",
                    entity_id=trip.trip_id,
                    source_file=trip.source_file,
                    source_row=trip.source_row,
                    related={"field": "shape_id", "value": trip.shape_id},
                )
            elif trip.trip_id not in graph.trip_to_shape_id:
                _add_issue(
                    findings,
                    severity="warning",
                    code="UNKNOWN_SHAPE_ID",
                    message=f"Trip {trip.trip_id} references unknown shape_id {trip.shape_id}",
                    entity_type="trip",
                    entity_id=trip.trip_id,
                    source_file=trip.source_file,
                    source_row=trip.source_row,
                    related={"field": "shape_id", "value": trip.shape_id},
                )

    for stop_time in feed.stop_times.values():
        if stop_time.trip_id not in feed.trips:
            _add_issue(
                findings,
                severity="error",
                code="UNKNOWN_TRIP_ID",
                message=(
                    f"Stop time {stop_time.stop_time_key} references unknown trip_id "
                    f"{stop_time.trip_id}"
                ),
                entity_type="stop_time",
                entity_id=stop_time.stop_time_key,
                source_file=stop_time.source_file,
                source_row=stop_time.source_row,
                related={"field": "trip_id", "value": stop_time.trip_id},
            )

        if stop_time.stop_id not in feed.stops:
            _add_issue(
                findings,
                severity="error",
                code="UNKNOWN_STOP_ID",
                message=(
                    f"Stop time {stop_time.stop_time_key} references unknown stop_id "
                    f"{stop_time.stop_id}"
                ),
                entity_type="stop_time",
                entity_id=stop_time.stop_time_key,
                source_file=stop_time.source_file,
                source_row=stop_time.source_row,
                related={"field": "stop_id", "value": stop_time.stop_id},
            )

    findings.sort(
        key=lambda issue: (
            0 if issue.severity == "error" else 1,
            issue.source_file,
            issue.source_row,
            issue.code,
        )
    )

    error_count = sum(issue.severity == "error" for issue in findings)
    if error_count:
        status: ValidationStatus = "invalid"
        written_artifacts = ["feed_summary.json", "validation_report.json"]
        suppressed_artifacts = ["normalized_entities.json", "relationships.json"]
    elif findings:
        status = "valid_with_warnings"
        written_artifacts = [
            "feed_summary.json",
            "normalized_entities.json",
            "relationships.json",
            "validation_report.json",
        ]
        suppressed_artifacts = []
    else:
        status = "valid"
        written_artifacts = [
            "feed_summary.json",
            "normalized_entities.json",
            "relationships.json",
            "validation_report.json",
        ]
        suppressed_artifacts = []

    return ValidationReport(
        status=status,
        findings=findings,
        missing_optional_files=list(bundle.missing_optional_files),
        written_artifacts=written_artifacts,
        suppressed_artifacts=suppressed_artifacts,
    )


def serialize_validation_report(report: ValidationReport) -> dict[str, object]:
    return {
        "status": report.status,
        "summary": {
            "error_count": report.error_count(),
            "warning_count": report.warning_count(),
        },
        "partial_ingestion": {
            "state": "raw_only" if report.status == "invalid" else "none",
            "reason": "fatal_validation_findings" if report.status == "invalid" else None,
            "written_artifacts": report.written_artifacts,
            "suppressed_artifacts": report.suppressed_artifacts,
        },
        "missing_optional_files": report.missing_optional_files,
        "findings": [asdict(issue) for issue in report.findings],
    }
