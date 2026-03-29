---
id: EP-20260329-001/MS002
execplan_id: EP-20260329-001
ms: 2
title: "Normalize GTFS entities and build baseline relationships"
status: planned
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

- [ ] Raw GTFS tables are preserved separately from normalized entities
- [ ] Normalized models exist for the core GTFS-static entities
- [ ] Baseline relationship graph covers the required GTFS chains
- [ ] Automated tests prove relationship counts and entity linking for the minimal feed
- [ ] The ingestion command prints a readable entity and relationship summary

## Scope

### In Scope

- Normalize `routes.txt`, `trips.txt`, `stops.txt`, `stop_times.txt`, `calendar.txt`, and `calendar_dates.txt`
- Support `shapes.txt` as an optional relationship source
- Build route to trips, trip to stop times, stop time to stop, trip to shape, and service identifier to calendar relationships
- Preserve source references so later validation can point back to the original file and row

### Out of Scope

- Database persistence
- HTTP APIs or frontend interfaces
- Advanced map geometry processing
- Performance optimization for large feeds

## Workstreams & Tasks

- Normalization layer: define stable internal entity models with one source of truth per entity type.
- Relationship layer: build a dedicated module that links normalized entities without reparsing raw data.
- Summary output: update the ingestion command so a developer can see entity counts and linked relationship counts in the terminal.
- Tests: add assertions covering successful relationship mapping on the valid minimal fixture.

## Risks & Mitigations

- Risk: Relationship construction may become tightly coupled to raw parsing logic.
  Mitigation: Require a separate relationship module that consumes normalized entities only.

- Risk: The system may accidentally assume optional files always exist.
  Mitigation: Keep optional relationships explicit and ensure tests cover feeds with and without `shapes.txt` and `calendar_dates.txt`.

## Validation / QA Plan

From the repository root, run:

    python -m pytest tests

Expected:

- The test run passes and includes assertions for normalized entity counts and relationship links.

Then run:

    python -m gtfs_visualizer.cli ingest sample-data/fixtures/minimal-static-feed --output-dir .tmp/ms002

Expected:

- The command exits with status `0`.
- The terminal prints normalized entity counts.
- The terminal confirms that route, trip, stop time, stop, and service relationships were built.

## Changelog

- 2026-03-29: Milestone created
