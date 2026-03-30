from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from gtfs_visualizer.ingest.feed_loader import load_feed
from gtfs_visualizer.models.normalized import normalize_feed
from gtfs_visualizer.relationships.linker import build_relationship_graph
from gtfs_visualizer.validation.report import validate_feed

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "sample-data" / "fixtures"


def test_validate_feed_reports_warning_only_for_missing_shapes_fixture() -> None:
    bundle = load_feed(FIXTURES_DIR / "missing-shapes-feed")
    feed = normalize_feed(bundle)
    graph = build_relationship_graph(feed)

    report = validate_feed(bundle, feed, graph)

    assert report.status == "valid_with_warnings"
    assert report.error_count() == 0
    assert report.warning_count() == 3
    assert {issue.code for issue in report.findings} == {
        "SHAPE_ID_WITHOUT_SHAPES_FILE",
        "MISSING_OPTIONAL_CALENDAR_DATES_FILE",
        "MISSING_OPTIONAL_SHAPES_FILE",
    }


def test_validate_feed_reports_invalid_relations_and_raw_only_partial_ingestion() -> None:
    temp_base = REPO_ROOT / ".tmp"
    temp_base.mkdir(parents=True, exist_ok=True)
    output_dir = temp_base / f"ms003-invalid-{uuid.uuid4().hex}"
    output_dir.mkdir(parents=True, exist_ok=False)
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "gtfs_visualizer.cli",
                "ingest",
                str(FIXTURES_DIR / "invalid-relations-feed"),
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 1
        assert "Validation: 4 errors, 3 warnings" in result.stdout
        assert "Error [UNKNOWN_ROUTE_ID]" in result.stdout

        assert (output_dir / "feed_summary.json").exists()
        assert (output_dir / "validation_report.json").exists()
        assert not (output_dir / "normalized_entities.json").exists()
        assert not (output_dir / "relationships.json").exists()

        validation_report = json.loads(
            (output_dir / "validation_report.json").read_text(encoding="utf-8")
        )
        assert validation_report["status"] == "invalid"
        assert validation_report["partial_ingestion"]["state"] == "raw_only"
        assert validation_report["partial_ingestion"]["written_artifacts"] == [
            "feed_summary.json",
            "validation_report.json",
        ]
        assert validation_report["partial_ingestion"]["suppressed_artifacts"] == [
            "normalized_entities.json",
            "relationships.json",
        ]
        assert {issue["code"] for issue in validation_report["findings"]} >= {
            "UNKNOWN_ROUTE_ID",
            "UNKNOWN_SERVICE_ID",
            "UNKNOWN_STOP_ID",
            "UNKNOWN_TRIP_ID",
        }
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_validate_feed_reports_duplicate_trip_id_with_data_row_source_row() -> None:
    temp_base = REPO_ROOT / ".tmp"
    temp_base.mkdir(parents=True, exist_ok=True)
    fixture_dir = temp_base / f"duplicate-trip-{uuid.uuid4().hex}"
    shutil.copytree(FIXTURES_DIR / "minimal-static-feed", fixture_dir)
    try:
        trips_path = fixture_dir / "trips.txt"
        trips_path.write_text(
            trips_path.read_text(encoding="utf-8") + "R1,WKD,T1,S1\n",
            encoding="utf-8",
        )

        bundle = load_feed(fixture_dir)
        feed = normalize_feed(bundle)
        graph = build_relationship_graph(feed)
        report = validate_feed(bundle, feed, graph)

        duplicate_trip_issue = next(
            issue for issue in report.findings if issue.code == "DUPLICATE_TRIP_ID"
        )
        assert duplicate_trip_issue.severity == "error"
        assert duplicate_trip_issue.source_file == "trips.txt"
        assert duplicate_trip_issue.source_row == 2
        assert duplicate_trip_issue.entity_id == "T1"
    finally:
        shutil.rmtree(fixture_dir, ignore_errors=True)


def test_validate_feed_reports_unknown_shape_id_when_shapes_file_exists() -> None:
    temp_base = REPO_ROOT / ".tmp"
    temp_base.mkdir(parents=True, exist_ok=True)
    fixture_dir = temp_base / f"unknown-shape-{uuid.uuid4().hex}"
    shutil.copytree(FIXTURES_DIR / "minimal-static-feed", fixture_dir)
    try:
        trips_path = fixture_dir / "trips.txt"
        trips_path.write_text(
            "route_id,service_id,trip_id,shape_id\nR1,WKD,T1,S_UNKNOWN\n",
            encoding="utf-8",
        )

        bundle = load_feed(fixture_dir)
        feed = normalize_feed(bundle)
        graph = build_relationship_graph(feed)
        report = validate_feed(bundle, feed, graph)

        unknown_shape_issue = next(
            issue for issue in report.findings if issue.code == "UNKNOWN_SHAPE_ID"
        )
        assert unknown_shape_issue.severity == "warning"
        assert unknown_shape_issue.source_file == "trips.txt"
        assert unknown_shape_issue.source_row == 1
        assert unknown_shape_issue.related == {"field": "shape_id", "value": "S_UNKNOWN"}
    finally:
        shutil.rmtree(fixture_dir, ignore_errors=True)
