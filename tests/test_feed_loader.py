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
    ]
    assert bundle.missing_optional_files == ["calendar_dates.txt"]
    assert bundle.row_counts() == {
        "routes": 1,
        "trips": 1,
        "stops": 2,
        "stop_times": 2,
        "calendar": 1,
        "shapes": 2,
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
        assert "Optional missing: calendar_dates.txt" in result.stdout

        summary = json.loads(
            (output_dir / "feed_summary.json").read_text(encoding="utf-8")
        )
        assert summary["loaded_files"][-1] == "shapes.txt"
        assert summary["row_counts"]["stop_times"] == 2
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
