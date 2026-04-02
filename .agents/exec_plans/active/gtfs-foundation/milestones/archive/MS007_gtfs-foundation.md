---
id: EP-20260329-001/MS007
execplan_id: EP-20260329-001
ms: 7
title: "Add deterministic graph index artifacts"
status: done
domain: backend
owner: "@codex"
created: 2026-04-02
updated: 2026-04-02
tags: [gtfs, graph, indexes, artifacts]
risk: med
links:
  issue: ""
  docs: ""
  pr: ""
---

# Add deterministic graph index artifacts

## Objective

Add a lightweight derived index layer over `graph_nodes.json` and `graph_edges.json` without changing graph read behavior. At the end of this milestone, the `graph` command also writes `graph_node_index.json` and `graph_edge_index.json`, while `graph-read` uses them read-only when present and falls back to the existing in-memory path when both are absent.

## Definition of Done

- [x] Graph index artifacts are generated only from `graph_nodes.json` and `graph_edges.json`
- [x] `graph_edge_index.json` does not contain an `adjacency` object
- [x] Graph index loading validates exact compatibility with the loaded graph artifacts
- [x] Partial index presence is treated as fatal
- [x] `graph-read` remains behavior-equivalent with and without indexes
- [x] Existing graph and graph-read contracts remain unchanged
- [x] Planning artifacts reflect completed MS007 state

## Scope

### In Scope

- Add deterministic node and edge index artifacts
- Add read-only index loading and exact graph-index compatibility validation
- Use source/target edge-position indexes for neighbor derivation when indexes are present
- Preserve fallback behavior when both index files are absent
- Add regression tests for stale, partial, extra, missing, and parity cases

### Out of Scope

- Any graph schema changes to `graph_nodes.json` or `graph_edges.json`
- Any UI, map, visualization, database, API, realtime, auth, deployment, or non-precomputation performance work
- Any ingest, normalization, validation, query, or raw GTFS reprocessing changes

## Workstreams & Tasks

- Graph index module: build, serialize, and validate `graph_node_index.json` and `graph_edge_index.json`.
- CLI integration: emit indexes from `graph`, load indexes from `graph-read`, and keep index usage strictly read-only.
- Service integration: consume precomputed source/target lookup structures when present and preserve current output ordering and deduplicated neighbor semantics.
- Planning hygiene and tests: record MS007 completion under `.agents` and extend graph regression coverage for exact compatibility and fallback parity.

## Risks & Mitigations

- Risk: Index artifacts drift from the graph artifacts and silently change read behavior.
  Mitigation: Validate index payloads against the expected serialized structure derived from the loaded graph bundle and fail on any mismatch.

- Risk: Partial index presence causes ambiguous mixed-mode reads.
  Mitigation: Treat the two index files as an atomic read pair: if one exists, both must exist and both must validate.

## Validation / QA Plan

From the repository root, run:

    .\.venv\Scripts\python.exe -m pytest tests

Expected:

- Existing ingest, query, graph, and graph-read tests still pass.
- New MS007 tests pass for exact index generation, partial-index failure, stale or mismatched indexes, missing or extra IDs, and indexed-versus-fallback parity.

## Changelog

- 2026-04-02: Milestone implemented and archived after adding deterministic graph index artifacts, exact compatibility validation, read-only index loading, and parity-focused graph regression tests.
