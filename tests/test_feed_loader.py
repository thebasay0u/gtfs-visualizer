from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from gtfs_visualizer.ingest.feed_loader import load_feed

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "sample-data" / "fixtures"


def test_load_feed_reads_required_and_optional_files() -> None:
    bundle = load_feed(FIXTURES_DIR / "minimal-static-feed")

    assert bundle.loaded_files == [
        "routes.txt",
        "trips.txt",
        "stops.txt",
        "stop_times.txt",
        "calendar.txt",
        "shapes.txt",
        "calendar_dates.txt",
    ]
    assert bundle.missing_optional_files == []
    assert bundle.row_counts() == {
        "routes": 1,
        "trips": 1,
        "stops": 2,
        "stop_times": 2,
        "calendar": 1,
        "shapes": 2,
        "calendar_dates": 1,
    }


def test_load_feed_allows_missing_optional_shapes() -> None:
    bundle = load_feed(FIXTURES_DIR / "missing-shapes-feed")

    assert bundle.missing_optional_files == ["shapes.txt", "calendar_dates.txt"]
    assert "shapes" not in bundle.tables


def test_cli_ingest_writes_summary_artifact() -> None:
    temp_base = REPO_ROOT / ".tmp"
    temp_base.mkdir(parents=True, exist_ok=True)
    temp_root = temp_base / f"ms001-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True, exist_ok=False)
    output_dir = temp_root / "artifacts"
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "gtfs_visualizer.cli",
                "ingest",
                str(FIXTURES_DIR / "minimal-static-feed"),
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 0
        assert "Feed loaded:" in result.stdout
        assert "Entities: routes=1, trips=1, stop_times=2, stops=2, services=1, shapes=1" in result.stdout
        assert (
            "Relationships: route_to_trips=1, trip_to_stop_times=2, stop_time_to_stops=2, "
            "trip_to_shapes=1, service_to_calendar=1"
        ) in result.stdout
        assert "Optional missing: none" in result.stdout
        assert "Validation: 0 errors, 0 warnings" in result.stdout

        summary = json.loads(
            (output_dir / "feed_summary.json").read_text(encoding="utf-8")
        )
        normalized_entities = json.loads(
            (output_dir / "normalized_entities.json").read_text(encoding="utf-8")
        )
        relationships = json.loads(
            (output_dir / "relationships.json").read_text(encoding="utf-8")
        )
        validation_report = json.loads(
            (output_dir / "validation_report.json").read_text(encoding="utf-8")
        )

        assert set(summary) == {
            "source_path",
            "loaded_files",
            "missing_optional_files",
            "row_counts",
        }
        assert summary["loaded_files"] == [
            "routes.txt",
            "trips.txt",
            "stops.txt",
            "stop_times.txt",
            "calendar.txt",
            "shapes.txt",
            "calendar_dates.txt",
        ]
        assert summary["row_counts"]["stop_times"] == 2
        assert normalized_entities["entity_counts"]["shapes"] == 1
        assert normalized_entities["entities"]["trips"]["T1"]["shape_id"] == "S1"
        assert relationships["missing_optional_files"] == []
        assert relationships["mappings"]["trip_to_shape_id"] == {"T1": "S1"}
        assert validation_report["status"] == "valid"
        assert validation_report["summary"] == {"error_count": 0, "warning_count": 0}
        assert validation_report["findings"] == []
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
