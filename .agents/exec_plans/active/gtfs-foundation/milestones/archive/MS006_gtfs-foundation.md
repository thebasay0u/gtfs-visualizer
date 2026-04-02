---
id: EP-20260329-001/MS006
execplan_id: EP-20260329-001
ms: 6
title: "Add graph-native read and traversal commands"
status: done
domain: backend
owner: "@codex"
created: 2026-03-30
updated: 2026-03-30
tags: [gtfs, graph, traversal, cli]
risk: med
links:
  issue: ""
  docs: ""
  pr: ""
---

# Add graph-native read and traversal commands

## Objective

Add a read-only graph access layer over `graph_nodes.json` and `graph_edges.json`. At the end of this milestone, a developer can inspect nodes, edges, and neighbors from generated graph artifacts through dedicated CLI commands without triggering graph regeneration or relying on query behavior.

## Definition of Done

- [x] Active ExecPlan reflects completed milestones through MS005 before MS006 implementation begins
- [x] MS004 and MS005 milestone documents are archived correctly
- [x] MS006 milestone document exists and is marked active prior to implementation
- [x] Graph artifacts load through a dedicated read-only graph loader
- [x] GraphService provides node lookup, edge lookup, filtering, and adjacency traversal
- [x] `graph-read` commands print deterministic JSON response shapes
- [x] Artifact failures and lookup failures remain separate
- [x] `registry.json` accurately reflects milestone and plan state after implementation

## Scope

### In Scope

- Read and validate `graph_nodes.json` and `graph_edges.json`
- Add graph-native node, edge, and neighbor access
- Add CLI-based graph inspection commands
- Keep neighbor outputs deduplicated by node while returning the full filtered edge set

### Out of Scope

- Graph generation changes
- UI, maps, graph visualization, APIs, persistence, auth, deployment, or performance work

## Workstreams & Tasks

- Planning hygiene: reconcile ExecPlan, milestone archive state, and registry before code changes.
- Graph artifact loading: add `GraphArtifactError`, `GraphBundle`, and graph-native validation.
- Graph service: add deterministic node, edge, and neighbor reads without depending on `QueryService`.
- CLI and tests: add `graph-read` commands with argparse-controlled filters and regression coverage.

## Risks & Mitigations

- Risk: Graph reads could accidentally regenerate missing artifacts.
  Mitigation: Make `graph-read` strictly fail on missing artifacts and never fall back to generation.

- Risk: Neighbor results could become nondeterministic or duplicate-heavy.
  Mitigation: Build adjacency from filtered edges, deduplicate neighbors by `node_id`, and sort deterministically.

## Validation / QA Plan

From the repository root, run:

    .\.venv\Scripts\python.exe -m pytest tests

Expected:

- Existing ingest, query, and graph-generation tests still pass.
- New graph-read tests pass for valid, warning-only, invalid, malformed, lookup, and CLI traversal scenarios.

## Changelog

- 2026-03-30: Milestone created and activated before implementation
- 2026-03-30: Milestone implemented and archived after adding graph artifact loading, `GraphService`, `graph-read` commands, and graph-read regression tests
