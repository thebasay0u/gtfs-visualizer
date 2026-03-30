from __future__ import annotations

from pathlib import Path

from gtfs_visualizer.ingest.feed_loader import load_feed
from gtfs_visualizer.models.normalized import normalize_feed
from gtfs_visualizer.relationships.linker import build_relationship_graph

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "sample-data" / "fixtures"


def test_normalize_feed_creates_inspectable_entities() -> None:
    feed = normalize_feed(load_feed(FIXTURES_DIR / "minimal-static-feed"))

    assert feed.entity_counts() == {
        "routes": 1,
        "trips": 1,
        "stop_times": 2,
        "stops": 2,
        "services": 1,
        "shapes": 1,
    }
    assert feed.routes["R1"].route_long_name == "Downtown Loop"
    assert feed.trips["T1"].service_id == "WKD"
    assert feed.stop_times["T1:1"].stop_id == "STOP1"
    assert feed.shapes["S1"][0].shape_pt_sequence == 1
    assert feed.services["WKD"].start_date == "20260101"


def test_build_relationship_graph_links_minimal_feed_entities() -> None:
    feed = normalize_feed(load_feed(FIXTURES_DIR / "minimal-static-feed"))

    graph = build_relationship_graph(feed)

    assert graph.route_to_trip_ids == {"R1": ["T1"]}
    assert graph.trip_to_route_id == {"T1": "R1"}
    assert graph.trip_to_stop_time_keys == {"T1": ["T1:1", "T1:2"]}
    assert graph.stop_time_key_to_stop_id == {
        "T1:1": "STOP1",
        "T1:2": "STOP2",
    }
    assert graph.trip_to_shape_id == {"T1": "S1"}
    assert graph.service_id_to_calendar_id == {"WKD": "WKD"}


def test_missing_optional_shapes_do_not_break_relationship_mapping() -> None:
    feed = normalize_feed(load_feed(FIXTURES_DIR / "missing-shapes-feed"))

    graph = build_relationship_graph(feed)

    assert feed.entity_counts()["shapes"] == 0
    assert "shapes.txt" in feed.missing_optional_files
    assert graph.trip_to_shape_id == {}
    assert graph.trip_to_stop_time_keys == {"T1": ["T1:1", "T1:2"]}
    assert graph.service_id_to_calendar_id == {"WKD": "WKD"}
