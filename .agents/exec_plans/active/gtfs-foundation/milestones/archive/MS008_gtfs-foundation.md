---
id: EP-20260329-001/MS008
execplan_id: EP-20260329-001
ms: 8
title: "Add route-level graph enrichment artifacts"
status: done
domain: backend
owner: "@codex"
created: 2026-04-03
updated: 2026-04-03
tags: [gtfs, graph, enrichment, artifacts]
risk: med
links:
  issue: ""
  docs: ""
  pr: ""
---

# Add route-level graph enrichment artifacts

## Objective

Add a generation-only enrichment layer that derives `route_serves_stop` edges from persisted graph and graph-index artifacts. At the end of this milestone, developers can run `graph-enrich` to produce `graph_enrichment_edges.json` without changing any existing ingest, query, graph, graph-read, or graph-index behavior.

## Definition of Done

- [x] `graph_enrich` remains generation-only and separate from `graph-read`
- [x] `graph_enrichment_edges.json` is derived strictly from graph and graph-index artifacts
- [x] Missing or invalid graph indexes fail with `GraphArtifactError`
- [x] `route_serves_stop` IDs are deterministic and independent of `trip_count`
- [x] `trip_count` counts unique trip node IDs only
- [x] Existing graph and graph-index contracts remain unchanged
- [x] A notebook tutorial exists under `notebooks/` for the new CLI flow
- [x] Planning artifacts reflect completed MS008 state

## Scope

### In Scope

- Add a dedicated graph enrichment builder and serializer
- Add the `graph-enrich` CLI command
- Add one shared-stop fixture to prove unique-trip counting with repeated stop visits
- Add tests for valid, warning-only, missing-index, stale-index, and shared-stop scenarios

### Out of Scope

- Any mutation of graph or graph-index artifacts
- Any graph-read integration, UI, map, visualization, API, persistence, auth, deployment, or realtime work
- Any ingestion, normalization, validation, or query behavior changes

## Workstreams & Tasks

- Enrichment builder: derive canonical `route_serves_stop` edges through index-driven traversal only.
- CLI: add `graph-enrich` as a strict consumer of existing graph and graph-index artifacts.
- Tests and fixtures: cover deterministic generation, fast failure on invalid prerequisites, and unique-trip counting.
- Tutorials and planning hygiene: add a short notebook walkthrough and synchronize `.agents` records with MS008 completion.

## Risks & Mitigations

- Risk: Enrichment might drift into a new source of graph truth.
  Mitigation: Keep enrichment in its own output artifact and do not integrate it into graph reads.

- Risk: Repeated stop visits could inflate `trip_count`.
  Mitigation: Count distinct trip node IDs per `(route, stop)` pair and prove the rule with a shared-stop fixture.

## Validation / QA Plan

From the repository root, run:

    .\.venv\Scripts\python.exe -m pytest tests

Expected:

- Existing test coverage still passes.
- New graph enrichment tests pass for deterministic output, shared-stop counting, and invalid-index failures.

## Changelog

- 2026-04-03: Milestone implemented and archived after adding `graph-enrich`, `graph_enrichment_edges.json`, a shared-stop fixture, graph enrichment tests, and a notebook tutorial.
