from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_GTFS_FILES = (
    "routes.txt",
    "trips.txt",
    "stops.txt",
    "stop_times.txt",
    "calendar.txt",
)
OPTIONAL_GTFS_FILES = (
    "shapes.txt",
    "calendar_dates.txt",
)


class FeedLoadError(Exception):
    """Raised when a GTFS-static feed cannot be loaded."""


@dataclass(slots=True)
class RawFeedBundle:
    source_path: Path
    tables: dict[str, pd.DataFrame]
    loaded_files: list[str]
    missing_optional_files: list[str]

    def row_counts(self) -> dict[str, int]:
        return {
            table_name: int(len(table))
            for table_name, table in self.tables.items()
        }


def load_feed(source_path: str | Path) -> RawFeedBundle:
    feed_path = Path(source_path).resolve()
    if not feed_path.exists():
        raise FeedLoadError(f"Feed path does not exist: {feed_path}")
    if not feed_path.is_dir():
        raise FeedLoadError(f"Feed path must be a directory: {feed_path}")

    missing_required = [
        file_name for file_name in REQUIRED_GTFS_FILES if not (feed_path / file_name).exists()
    ]
    if missing_required:
        missing_list = ", ".join(missing_required)
        raise FeedLoadError(
            f"Missing required GTFS files in {feed_path}: {missing_list}"
        )

    tables: dict[str, pd.DataFrame] = {}
    loaded_files: list[str] = []
    for file_name in REQUIRED_GTFS_FILES + OPTIONAL_GTFS_FILES:
        file_path = feed_path / file_name
        if not file_path.exists():
            continue
        tables[file_name[:-4]] = pd.read_csv(file_path, dtype=str, keep_default_na=False)
        loaded_files.append(file_name)

    missing_optional_files = [
        file_name for file_name in OPTIONAL_GTFS_FILES if file_name not in loaded_files
    ]

    return RawFeedBundle(
        source_path=feed_path,
        tables=tables,
        loaded_files=loaded_files,
        missing_optional_files=missing_optional_files,
    )
