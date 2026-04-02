---
id: EP-20260329-001/MS004
execplan_id: EP-20260329-001
ms: 4
title: "Add artifact-backed relationship query layer"
status: done
domain: backend
owner: "@codex"
created: 2026-03-30
updated: 2026-03-30
tags: [gtfs, query, cli, consumer]
risk: med
links:
  issue: ""
  docs: ""
  pr: ""
---

# Add artifact-backed relationship query layer

## Objective

Provide the first consumer-facing interface above validated GTFS artifacts. At the end of this milestone, a developer can query route, trip, and stop detail from a valid or warning-only artifact directory without re-reading the source feed.

## Definition of Done

- [x] Query artifacts load from valid and warning-only bundles
- [x] Route, trip, and stop queries return fixed JSON response shapes
- [x] Query failures use explicit artifact and lookup error classes
- [x] CLI prints query errors to stderr and returns exit code `1`
- [x] Tests cover loader, service, and CLI behavior

## Scope

### In Scope

- Add a read-only query layer that consumes `validation_report.json`, `normalized_entities.json`, and `relationships.json`
- Support `query routes`, `query route <id>`, `query trip <id>`, and `query stop <id>`
- Validate minimum required artifact keys while ignoring unknown extra keys
- Return `service: null` when unavailable and always include `shape_points` as a list

### Out of Scope

- New ingest artifacts
- Visualization-specific data preparation
- Database persistence, HTTP APIs, auth, deployment, or performance work

## Workstreams & Tasks

- Artifact loading: add `QueryBundle` and `QueryArtifactError` with minimum-structure validation.
- Query service: add read-only route, trip, and stop detail assembly plus `QueryLookupError`.
- CLI: add the `query` command family with stderr error handling and JSON stdout responses.
- Tests: prove valid, warning-only, invalid, malformed, and unknown-ID behavior.

## Risks & Mitigations

- Risk: The query layer could become coupled to ingestion internals.
  Mitigation: Consume serialized artifacts only and avoid calling ingest, normalization, or validation code from query logic.

- Risk: Artifact validation could become brittle as artifacts evolve.
  Mitigation: Validate only the minimum required keys and ignore unknown extra keys.

## Validation / QA Plan

From the repository root, run:

    .\.venv\Scripts\python.exe -m pytest tests

Expected:

- Existing MS001-MS003 tests still pass.
- New query tests pass for valid, warning-only, invalid, malformed, and CLI scenarios.

## Changelog

- 2026-03-30: Milestone created
- 2026-03-30: Milestone implemented and archived after adding the artifact-backed query loader, `QueryService`, `query` CLI commands, and regression coverage
