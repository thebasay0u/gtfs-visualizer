---
id: EP-20260329-001/MS003
execplan_id: EP-20260329-001
ms: 3
title: "Surface validation outcomes and partial-ingestion behavior"
status: done
domain: backend
owner: "@codex"
created: 2026-03-29
updated: 2026-03-29
tags: [gtfs, validation, errors, qa]
risk: med
links:
  issue: ""
  docs: ""
  pr: ""
---

# Surface validation outcomes and partial-ingestion behavior

## Objective

Make feed quality visible and trustworthy. At the end of this milestone, the ingestion workflow should produce a structured validation report that distinguishes warnings from errors, identifies the source of broken relationships, and makes partial-ingestion behavior explicit for malformed or incomplete GTFS-static feeds.

## Definition of Done

- [x] Validation issues are reported with severity, fixed code, message, entity context, and source reference
- [x] Broken foreign-key relationships are surfaced clearly
- [x] Partial-ingestion behavior is defined and observable
- [x] Automated tests cover clean, warning-only, broken, duplicate, and unknown-shape scenarios
- [x] The ingestion command returns clear success and failure exit behavior

## Scope

### In Scope

- Validate orphan records, missing optional files, duplicate identifiers, and inconsistent service references
- Emit structured validation artifacts to the chosen output directory
- Return terminal summaries and exit statuses that distinguish warnings from errors
- Preserve enough source context to help a developer debug broken feeds quickly
- Suppress `normalized_entities.json` and `relationships.json` when validation status is `invalid`

### Out of Scope

- UI-based error presentation
- Feed editing or repair tools
- Large-feed performance work
- Production deployment concerns

## Workstreams & Tasks

- Validation contract: define issue severity levels and report structure.
- Broken-feed fixtures: add at least one fixture with invalid relationships and one fixture with duplicate or conflicting identifiers.
- Broken-feed fixtures: add at least one permanent invalid-relationships fixture and use temporary copied fixtures for duplicate and unknown-shape cases.
- Error surfacing: update the ingestion command to print concise summaries and write detailed report artifacts.
- Tests: verify that valid feeds succeed, warning-only feeds succeed with warnings, and error-containing feeds fail clearly.

## Risks & Mitigations

- Risk: Partial ingestion could hide serious data integrity problems.
  Mitigation: Require explicit severity rules and never label a feed fully valid when required relationship chains are broken.

- Risk: Validation output could become too noisy to be actionable.
  Mitigation: Keep terminal output concise and store detailed per-issue artifacts in the output directory for deeper inspection.

## Validation / QA Plan

From the repository root, run:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -e .[dev]
    python -m pytest tests

Expected:

- The test run passes and includes broken-feed scenarios for orphan references, inconsistent service identifiers, and duplicate identifiers.

Then run:

    .\.venv\Scripts\Activate.ps1
    python -m gtfs_visualizer.cli ingest sample-data/fixtures/minimal-static-feed --output-dir .tmp/ms003-valid
    python -m gtfs_visualizer.cli ingest sample-data/fixtures/missing-shapes-feed --output-dir .tmp/ms003-warning
    python -m gtfs_visualizer.cli ingest sample-data/fixtures/invalid-relations-feed --output-dir .tmp/ms003-invalid

Expected:

- The valid command exits with status `0` and writes `feed_summary.json`, `normalized_entities.json`, `relationships.json`, and `validation_report.json`.
- The warning-only command exits with status `0` and writes the same four artifacts.
- The invalid command exits with status `1`.
- The invalid command writes `feed_summary.json` and `validation_report.json` only.
- The invalid command does not write `normalized_entities.json` or `relationships.json`.
- `validation_report.json` records fixed v1 codes and uses `source_row` as the 1-based data row number excluding the header row.

## Changelog

- 2026-03-29: Milestone created
- 2026-03-29: Milestone implemented, validated, and archived after adding the validation layer, fixed v1 codes, partial-ingestion policy, invalid artifact suppression, and ten passing tests
