from __future__ import annotations

import argparse
import json
from pathlib import Path

from gtfs_visualizer.ingest.feed_loader import FeedLoadError, load_feed
from gtfs_visualizer.models.normalized import normalize_feed, serialize_normalized_feed
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "ingest":
            return run_ingest(args.feed_path, args.output_dir)
    except FeedLoadError as exc:
        print(f"Error: {exc}")
        return 1

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
