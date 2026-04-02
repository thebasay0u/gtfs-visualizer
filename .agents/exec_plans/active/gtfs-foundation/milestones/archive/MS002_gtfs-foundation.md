---
id: EP-20260329-001/MS002
execplan_id: EP-20260329-001
ms: 2
title: "Normalize GTFS entities and build baseline relationships"
status: done
domain: backend
owner: "@codex"
created: 2026-03-29
updated: 2026-03-29
tags: [gtfs, normalization, relationships]
risk: med
links:
  issue: ""
  docs: ""
  pr: ""
---

# Normalize GTFS entities and build baseline relationships

## Objective

Introduce the internal data backbone for the GTFS Visualizer App. At the end of this milestone, a valid minimal GTFS-static feed should be transformed from raw tables into normalized entities and a baseline relationship graph that directly expresses the required route, trip, stop time, stop, shape, and service calendar links.

## Definition of Done

- [x] Raw GTFS tables are preserved separately from normalized entities
- [x] Normalized models exist for the core GTFS-static entities
- [x] Baseline relationship graph covers the required GTFS chains
- [x] `normalized_entities.json` and `relationships.json` are written without changing the existing `feed_summary.json` contract
- [x] Automated tests prove relationship counts and entity linking for the minimal feed
- [x] The ingestion command prints a readable entity and relationship summary

## Scope

### In Scope

- Normalize `routes.txt`, `trips.txt`, `stops.txt`, `stop_times.txt`, and `calendar.txt`
- Support `shapes.txt` as an optional relationship source
- Build route to trips, trip to stop times, stop time to stop, trip to shape, and service identifier to calendar relationships
- Preserve source references so later validation can point back to the original file and row
- Keep `feed_summary.json` unchanged while adding `normalized_entities.json` for normalized inspection and `relationships.json` for relationship mappings

### Out of Scope

- Database persistence
- HTTP APIs or frontend interfaces
- Advanced map geometry processing
- Performance optimization for large feeds

## Workstreams & Tasks

- Normalization layer: define stable internal entity models with one source of truth per entity type.
- Relationship layer: build a dedicated module that links normalized entities without reparsing raw data.
- Summary output: update the ingestion command so a developer can see entity counts and linked relationship counts in the terminal.
- Inspection artifacts: write normalized entity data and relationship mappings to separate JSON files for debugging.
- Tests: add assertions covering successful relationship mapping on the valid minimal fixture.

## Risks & Mitigations

- Risk: Relationship construction may become tightly coupled to raw parsing logic.
  Mitigation: Require a separate relationship module that consumes normalized entities only.

- Risk: The system may accidentally assume optional files always exist.
  Mitigation: Keep optional relationships explicit and ensure tests cover feeds with and without `shapes.txt` and `calendar_dates.txt`.

## Validation / QA Plan

From the repository root, run:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -e .[dev]
    python -m pytest tests

Expected:

- The test run passes and includes assertions for normalized entity counts and relationship links.

Then run:

    .\.venv\Scripts\Activate.ps1
    python -m gtfs_visualizer.cli ingest sample-data/fixtures/minimal-static-feed --output-dir .tmp/ms002
    python -m gtfs_visualizer.cli ingest sample-data/fixtures/missing-shapes-feed --output-dir .tmp/ms002-missing-shapes

Expected:

- The command exits with status `0`.
- The terminal prints normalized entity counts.
- The terminal confirms that route, trip, stop time, stop, and service relationships were built.
- `.tmp/ms002/feed_summary.json` is unchanged in shape from MS001.
- `.tmp/ms002/normalized_entities.json` exists and contains normalized entity counts plus inspectable normalized entity structures.
- `.tmp/ms002/relationships.json` exists and contains only relationship mappings plus directly relevant metadata such as `missing_optional_files`.
- `.tmp/ms002-missing-shapes/relationships.json` shows no trip-to-shape mappings and lists `shapes.txt` under `missing_optional_files`.

## Changelog

- 2026-03-29: Milestone created
- 2026-03-29: Milestone implemented, validated, and archived after adding normalized GTFS entity models, baseline relationship mapping, the split inspection artifacts, and six passing fixture-driven tests
