---
id: EP-20260329-001/MS001
execplan_id: EP-20260329-001
ms: 1
title: "Establish local ingestion workflow and repository skeleton"
status: done
domain: backend
owner: "@codex"
created: 2026-03-29
updated: 2026-03-29
tags: [gtfs, workflow, fixtures, ingestion]
risk: low
links:
  issue: ""
  docs: ""
  pr: ""
---

# Establish local ingestion workflow and repository skeleton

## Objective

Create the first independently runnable foundation for the repository. At the end of this milestone, a developer should be able to install local dependencies, run one standard test command, and execute a single ingestion entry point against a minimal GTFS-static fixture feed without needing a database, a browser, or deployment infrastructure.

## Definition of Done

- [x] Repository-local Python workflow is defined and executable
- [x] Minimal GTFS-static fixture feed exists under `sample-data/fixtures/`
- [x] A single ingestion entry point loads a feed path from disk
- [x] After activating the repository virtual environment, `python -m pytest tests` runs successfully from the repository root
- [x] Behavior is observable through terminal output

## Scope

### In Scope

- Create the Python package skeleton under `src/gtfs_visualizer/`
- Create the initial test layout under `tests/`
- Add fixture feeds for one valid minimal GTFS-static feed and one feed with a missing optional file
- Define the first local ingestion command contract and terminal summary
- Define the repository-local Windows PowerShell virtual environment workflow needed to run the command and test loop

### Out of Scope

- Full normalized entity models
- Relationship graph construction beyond basic feed loading confirmation
- Structured validation severity rules
- Frontend, map rendering, graph visualization, auth, deployment, or GTFS-realtime

## Workstreams & Tasks

- Workflow foundation: define the local Python project structure, dependency declaration, and repeatable test command.
- Fixture foundation: add small GTFS-static fixture directories that are easy to inspect by hand.
- Ingestion contract: implement a feed loader entry point that can locate required GTFS files and report missing required files clearly.
- Test foundation: add the first tests proving the entry point can load a valid fixture and handle an omitted optional file without crashing.

## Risks & Mitigations

- Risk: The repository could accumulate scaffolding that does not match the later domain model.
  Mitigation: Keep this milestone thin and define only the entry points and directory structure needed by later milestones.

- Risk: Fixture feeds may be too large or too vague to serve as reliable proofs.
  Mitigation: Use intentionally tiny feeds with handwritten records and explicit comments in tests describing what each fixture proves.

## Validation / QA Plan

From the repository root, run:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -e .[dev]
    python -m pytest tests

Expected:

- The test run passes.
- At least one test proves a valid minimal feed path can be loaded successfully.
- At least one test proves a missing optional file such as `shapes.txt` is reported as non-fatal behavior.

Then run:

    .\.venv\Scripts\Activate.ps1
    python -m gtfs_visualizer.cli ingest sample-data/fixtures/minimal-static-feed --output-dir .tmp/ms001

Expected:

- The command exits with status `0`.
- The terminal confirms that the feed path was read successfully and reports raw row counts.
- The command does not yet need to emit a full relationship summary.

## Changelog

- 2026-03-29: Milestone created
- 2026-03-29: Milestone implemented, validated, and archived after adding the local virtual environment workflow, raw feed loader, fixture feeds, and passing tests
