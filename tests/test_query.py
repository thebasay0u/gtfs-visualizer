from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from gtfs_visualizer.query import QueryArtifactError, QueryLookupError, QueryService, load_query_bundle

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "sample-data" / "fixtures"


def _ingest_fixture(fixture_name: str, prefix: str) -> Path:
    temp_base = REPO_ROOT / ".tmp"
    temp_base.mkdir(parents=True, exist_ok=True)
    output_dir = temp_base / f"{prefix}-{uuid.uuid4().hex}"
    output_dir.mkdir(parents=True, exist_ok=False)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gtfs_visualizer.cli",
            "ingest",
            str(FIXTURES_DIR / fixture_name),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode in {0, 1}
    return output_dir


def test_load_query_bundle_accepts_valid_and_warning_only_bundles() -> None:
    valid_dir = _ingest_fixture("minimal-static-feed", "ms004-valid")
    warning_dir = _ingest_fixture("missing-shapes-feed", "ms004-warning")
    try:
        valid_bundle = load_query_bundle(valid_dir)
        warning_bundle = load_query_bundle(warning_dir)

        assert valid_bundle.route_to_trip_ids == {"R1": ["T1"]}
        assert warning_bundle.trip_to_shape_id == {}
    finally:
        shutil.rmtree(valid_dir, ignore_errors=True)
        shutil.rmtree(warning_dir, ignore_errors=True)


def test_load_query_bundle_rejects_invalid_raw_only_bundle() -> None:
    invalid_dir = _ingest_fixture("invalid-relations-feed", "ms004-invalid")
    try:
        try:
            load_query_bundle(invalid_dir)
        except QueryArtifactError as exc:
            assert "invalid/raw-only" in str(exc)
        else:
            raise AssertionError("Expected QueryArtifactError for invalid bundle")
    finally:
        shutil.rmtree(invalid_dir, ignore_errors=True)


def test_load_query_bundle_rejects_missing_artifact_files() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms004-missing-file")
    try:
        (output_dir / "relationships.json").unlink()

        try:
            load_query_bundle(output_dir)
        except QueryArtifactError as exc:
            assert "relationships.json" in str(exc)
        else:
            raise AssertionError("Expected QueryArtifactError for missing artifact")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_load_query_bundle_rejects_missing_required_keys_or_malformed_structure() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms004-malformed")
    try:
        normalized_path = output_dir / "normalized_entities.json"
        normalized_data = json.loads(normalized_path.read_text(encoding="utf-8"))
        normalized_data["extra"] = {"ignored": True}
        del normalized_data["entities"]["routes"]
        normalized_path.write_text(json.dumps(normalized_data, indent=2), encoding="utf-8")

        try:
            load_query_bundle(output_dir)
        except QueryArtifactError as exc:
            assert "entities.routes" in str(exc)
        else:
            raise AssertionError("Expected QueryArtifactError for malformed structure")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_load_query_bundle_ignores_unknown_extra_keys() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms004-extra-keys")
    try:
        relationships_path = output_dir / "relationships.json"
        relationships_data = json.loads(relationships_path.read_text(encoding="utf-8"))
        relationships_data["ignored_top_level"] = {"x": 1}
        relationships_path.write_text(
            json.dumps(relationships_data, indent=2),
            encoding="utf-8",
        )

        bundle = load_query_bundle(output_dir)

        assert bundle.route_to_trip_ids == {"R1": ["T1"]}
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_query_service_returns_locked_route_trip_and_stop_shapes() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms004-service")
    try:
        service = QueryService(load_query_bundle(output_dir))

        routes = service.list_routes()
        route_detail = service.get_route_detail("R1")
        trip_detail = service.get_trip_detail("T1")
        stop_detail = service.get_stop_detail("STOP1")

        assert list(routes) == ["routes"]
        assert list(routes["routes"][0]) == ["route", "trip_count"]
        assert route_detail == {"route": route_detail["route"], "trip_ids": ["T1"], "trip_count": 1}
        assert list(trip_detail) == ["trip", "route", "service", "shape_points", "stops"]
        assert trip_detail["service"]["service_id"] == "WKD"
        assert trip_detail["shape_points"][0]["shape_id"] == "S1"
        assert trip_detail["stops"][0]["stop_time"]["stop_time_key"] == "T1:1"
        assert trip_detail["stops"][0]["stop"]["stop_id"] == "STOP1"
        assert list(stop_detail) == ["stop", "visits", "route_ids", "trip_ids"]
        assert stop_detail["route_ids"] == ["R1"]
        assert stop_detail["trip_ids"] == ["T1"]
        assert stop_detail["visits"][0]["route_id"] == "R1"
        assert stop_detail["visits"][0]["trip_id"] == "T1"
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_query_service_returns_empty_shape_points_and_null_service_when_unavailable() -> None:
    output_dir = _ingest_fixture("missing-shapes-feed", "ms004-missing-shape")
    try:
        normalized_path = output_dir / "normalized_entities.json"
        normalized_data = json.loads(normalized_path.read_text(encoding="utf-8"))
        del normalized_data["entities"]["services"]["WKD"]
        normalized_path.write_text(json.dumps(normalized_data, indent=2), encoding="utf-8")

        service = QueryService(load_query_bundle(output_dir))
        trip_detail = service.get_trip_detail("T1")

        assert trip_detail["service"] is None
        assert trip_detail["shape_points"] == []
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_query_service_raises_lookup_error_for_unknown_ids() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms004-lookup")
    try:
        service = QueryService(load_query_bundle(output_dir))

        for method, entity_id in [
            (service.get_route_detail, "R_UNKNOWN"),
            (service.get_trip_detail, "T_UNKNOWN"),
            (service.get_stop_detail, "STOP_UNKNOWN"),
        ]:
            try:
                method(entity_id)
            except QueryLookupError:
                pass
            else:
                raise AssertionError("Expected QueryLookupError")
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_query_commands_emit_locked_top_level_json_shapes() -> None:
    output_dir = _ingest_fixture("minimal-static-feed", "ms004-cli-success")
    try:
        expectations = [
            (["routes"], ["routes"]),
            (["route", "R1"], ["route", "trip_ids", "trip_count"]),
            (["trip", "T1"], ["trip", "route", "service", "shape_points", "stops"]),
            (["stop", "STOP1"], ["stop", "visits", "route_ids", "trip_ids"]),
        ]

        for args, expected_keys in expectations:
            result = subprocess.run(
                [sys.executable, "-m", "gtfs_visualizer.cli", "query", str(output_dir), *args],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                check=False,
            )
            assert result.returncode == 0
            assert result.stderr == ""
            payload = json.loads(result.stdout)
            assert list(payload) == expected_keys
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_cli_query_failures_print_to_stderr_and_exit_one() -> None:
    valid_dir = _ingest_fixture("minimal-static-feed", "ms004-cli-failure")
    invalid_dir = _ingest_fixture("invalid-relations-feed", "ms004-cli-invalid")
    try:
        lookup_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "gtfs_visualizer.cli",
                "query",
                str(valid_dir),
                "route",
                "R_UNKNOWN",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )
        artifact_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "gtfs_visualizer.cli",
                "query",
                str(invalid_dir),
                "routes",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert lookup_result.returncode == 1
        assert lookup_result.stdout == ""
        assert "Unknown route_id" in lookup_result.stderr

        assert artifact_result.returncode == 1
        assert artifact_result.stdout == ""
        assert "invalid/raw-only" in artifact_result.stderr
    finally:
        shutil.rmtree(valid_dir, ignore_errors=True)
        shutil.rmtree(invalid_dir, ignore_errors=True)
