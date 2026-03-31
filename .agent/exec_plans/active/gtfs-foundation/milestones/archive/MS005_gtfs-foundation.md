---
id: EP-20260329-001/MS005
execplan_id: EP-20260329-001
ms: 5
title: "Add graph-ready visualization prep artifacts"
status: done
domain: backend
owner: "@codex"
created: 2026-03-30
updated: 2026-03-30
tags: [gtfs, graph, artifacts, visualization]
risk: med
links:
  issue: ""
  docs: ""
  pr: ""
---

# Add graph-ready visualization prep artifacts

## Objective

Add a visualization-prep layer that transforms validated artifacts into deterministic graph-ready node and edge artifacts. At the end of this milestone, a developer can generate `graph_nodes.json` and `graph_edges.json` from a valid or warning-only artifact bundle without changing query behavior.

## Definition of Done

- [x] Graph generation consumes existing validated artifacts only
- [x] Graph artifacts are produced only for valid or warning-only bundles
- [x] The graph contract is minimal and deterministic
- [x] Existing query behavior remains unchanged
- [x] Tests cover valid, warning-only, invalid, and compatibility scenarios

## Scope

### In Scope

- Add graph node and edge serialization for routes, trips, and stops
- Add `route_has_trip` and `trip_stops_at` edge generation
- Add a narrow `graph` CLI command to write graph artifacts
- Keep graph generation read-only with respect to upstream GTFS processing

### Out of Scope

- Graph traversal or graph-native reads
- UI, map rendering, or graph visualization
- Database persistence, APIs, auth, deployment, or performance work

## Workstreams & Tasks

- Shared artifact loading: extract neutral validated artifact loading for reuse beyond query.
- Graph builder: add deterministic node and edge generation with fixed JSON contracts.
- CLI: add graph artifact generation without changing `ingest` or `query`.
- Tests: cover graph schema, ordering, gating, and query compatibility.

## Risks & Mitigations

- Risk: The graph layer could drift into query or UI behavior.
  Mitigation: Keep the schema minimal, deterministic, and artifact-generation only.

- Risk: Reusing query loading directly would couple graph prep to query semantics.
  Mitigation: Extract neutral validated artifact loading and keep query as a wrapper.

## Validation / QA Plan

From the repository root, run:

    .\.venv\Scripts\python.exe -m pytest tests

Expected:

- Existing MS001-MS004 tests still pass.
- Graph tests pass for valid, warning-only, invalid, and compatibility scenarios.

## Changelog

- 2026-03-30: Milestone created and implemented after adding shared validated artifact loading, graph artifact generation, the `graph` CLI command, and graph regression tests
