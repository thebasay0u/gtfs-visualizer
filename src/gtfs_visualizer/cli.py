from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from gtfs_visualizer.ingest.feed_loader import FeedLoadError, load_feed
from gtfs_visualizer.graph import build_graph_artifacts, serialize_graph_edges, serialize_graph_nodes
from gtfs_visualizer.models.normalized import normalize_feed, serialize_normalized_feed
from gtfs_visualizer.query import (
    QueryArtifactError,
    QueryLookupError,
    QueryService,
    load_query_bundle,
)
from gtfs_visualizer.relationships.linker import (
    build_relationship_graph,
    serialize_relationship_graph,
)
from gtfs_visualizer.validation.report import serialize_validation_report, validate_feed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gtfs_visualizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Load a GTFS-static feed from disk and emit a raw ingestion summary.",
    )
    ingest_parser.add_argument("feed_path", help="Path to a GTFS-static directory.")
    ingest_parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where ingestion artifacts will be written.",
    )

    query_parser = subparsers.add_parser(
        "query",
        help="Query previously generated GTFS artifact bundles.",
    )
    query_parser.add_argument("artifacts_dir", help="Directory containing queryable artifacts.")
    query_subparsers = query_parser.add_subparsers(dest="query_command", required=True)
    query_subparsers.add_parser("routes", help="List all routes with trip counts.")

    route_parser = query_subparsers.add_parser("route", help="Show route detail.")
    route_parser.add_argument("route_id", help="Route identifier.")

    trip_parser = query_subparsers.add_parser("trip", help="Show trip detail.")
    trip_parser.add_argument("trip_id", help="Trip identifier.")

    stop_parser = query_subparsers.add_parser("stop", help="Show stop detail.")
    stop_parser.add_argument("stop_id", help="Stop identifier.")

    graph_parser = subparsers.add_parser(
        "graph",
        help="Generate graph-ready artifacts from a validated artifact bundle.",
    )
    graph_parser.add_argument("artifacts_dir", help="Directory containing queryable artifacts.")
    graph_parser.add_argument(
        "--output-dir",
        help="Directory where graph artifacts will be written. Defaults to the artifacts directory.",
    )

    return parser


def run_ingest(feed_path: str, output_dir: str) -> int:
    bundle = load_feed(feed_path)
    normalized_feed = normalize_feed(bundle)
    relationship_graph = build_relationship_graph(normalized_feed)
    validation_report = validate_feed(bundle, normalized_feed, relationship_graph)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary = {
        "source_path": str(bundle.source_path),
        "loaded_files": bundle.loaded_files,
        "missing_optional_files": bundle.missing_optional_files,
        "row_counts": bundle.row_counts(),
    }
    summary_path = output_path / "feed_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    validation_path = output_path / "validation_report.json"
    validation_path.write_text(
        json.dumps(serialize_validation_report(validation_report), indent=2),
        encoding="utf-8",
    )

    if validation_report.status != "invalid":
        normalized_entities_path = output_path / "normalized_entities.json"
        normalized_entities_path.write_text(
            json.dumps(serialize_normalized_feed(normalized_feed), indent=2),
            encoding="utf-8",
        )

        relationships_path = output_path / "relationships.json"
        relationships_path.write_text(
            json.dumps(
                serialize_relationship_graph(
                    relationship_graph,
                    missing_optional_files=bundle.missing_optional_files,
                ),
                indent=2,
            ),
            encoding="utf-8",
        )

    print(f"Feed loaded: {Path(feed_path)}")
    print("Loaded files: " + ", ".join(bundle.loaded_files))
    print(
        "Rows: "
        + ", ".join(
            f"{table_name}={row_count}"
            for table_name, row_count in summary["row_counts"].items()
        )
    )
    if validation_report.status != "invalid":
        print(
            "Entities: "
            + ", ".join(
                f"{entity_name}={entity_count}"
                for entity_name, entity_count in normalized_feed.entity_counts().items()
            )
        )
        print(
            "Relationships: "
            + ", ".join(
                f"{name}={count}"
                for name, count in relationship_graph.relationship_counts().items()
            )
        )
    if bundle.missing_optional_files:
        print("Optional missing: " + ", ".join(bundle.missing_optional_files))
    else:
        print("Optional missing: none")
    print(
        f"Validation: {validation_report.error_count()} errors, "
        f"{validation_report.warning_count()} warnings"
    )
    for issue in validation_report.findings:
        label = "Error" if issue.severity == "error" else "Warning"
        print(f"{label} [{issue.code}]: {issue.message}")
    print(f"Output written to {summary_path}")
    return 1 if validation_report.status == "invalid" else 0


def run_query(artifacts_dir: str, query_command: str, identifier: str | None = None) -> int:
    bundle = load_query_bundle(Path(artifacts_dir))
    service = QueryService(bundle)

    if query_command == "routes":
        payload = service.list_routes()
    elif query_command == "route":
        if identifier is None:
            raise QueryArtifactError("Missing required route identifier")
        payload = service.get_route_detail(identifier)
    elif query_command == "trip":
        if identifier is None:
            raise QueryArtifactError("Missing required trip identifier")
        payload = service.get_trip_detail(identifier)
    elif query_command == "stop":
        if identifier is None:
            raise QueryArtifactError("Missing required stop identifier")
        payload = service.get_stop_detail(identifier)
    else:
        raise QueryArtifactError(f"Unsupported query command: {query_command}")

    print(json.dumps(payload, indent=2))
    return 0


def run_graph(artifacts_dir: str, output_dir: str | None = None) -> int:
    bundle = load_query_bundle(Path(artifacts_dir))
    graph = build_graph_artifacts(bundle)

    destination = Path(output_dir) if output_dir is not None else Path(artifacts_dir)
    destination.mkdir(parents=True, exist_ok=True)

    nodes_path = destination / "graph_nodes.json"
    nodes_path.write_text(json.dumps(serialize_graph_nodes(graph), indent=2), encoding="utf-8")

    edges_path = destination / "graph_edges.json"
    edges_path.write_text(json.dumps(serialize_graph_edges(graph), indent=2), encoding="utf-8")

    print(f"Graph artifacts written: {nodes_path}, {edges_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "ingest":
            return run_ingest(args.feed_path, args.output_dir)
        if args.command == "query":
            identifier = None
            if args.query_command == "route":
                identifier = args.route_id
            elif args.query_command == "trip":
                identifier = args.trip_id
            elif args.query_command == "stop":
                identifier = args.stop_id
            return run_query(args.artifacts_dir, args.query_command, identifier)
        if args.command == "graph":
            return run_graph(args.artifacts_dir, args.output_dir)
    except FeedLoadError as exc:
        print(f"Error: {exc}")
        return 1
    except (QueryArtifactError, QueryLookupError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
