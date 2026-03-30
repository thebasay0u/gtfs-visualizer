---
id: EP-20260329-001
title: "Establish GTFS static foundation"
status: active
kind: feature
domain: cross-cutting
owner: "@codex"
created: 2026-03-29
updated: 2026-03-30
tags: [gtfs, foundation, ingestion, modeling, validation, workflow]
touches: [api, db, cli, tests, docs, agents]
risk: med
breaking: false
migration: false
links:
  issue: ""
  pr: ""
  docs: ""
depends_on: []
supersedes: []
---

# Establish GTFS static foundation

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. This document must be maintained in accordance with `PLANS.md` at the repository root.

## Purpose / Big Picture

This plan establishes the first working backbone of the GTFS Visualizer App. After this plan is implemented, a developer should be able to run a local ingestion command against a GTFS-static feed, see a normalized representation of the core entities, inspect a baseline relationship graph that links routes to trips, trips to stop times, stop times to stops, trips to shapes when present, and service identifiers to calendar data, and receive a structured validation report that distinguishes fatal errors from warnings.

The first user-visible proof point is intentionally local and backend-first. A developer working in this repository should be able to run a repeatable command in the repository root against fixture feeds in `sample-data/`, observe a clear success or failure summary in the terminal, and verify that normalized outputs and validation artifacts were produced without needing a user interface, deployment environment, authentication, or GTFS-realtime support.

## Progress

- [x] (2026-03-29T20:04:11Z) Read `AGENTS.md` and `PLANS.md`, confirmed that no prior ExecPlans or milestones exist, and reserved `EP-20260329-001` as the first canonical plan ID for this repository.
- [x] (2026-03-29T20:04:11Z) Authored this ExecPlan and defined the initial milestone set `MS001` through `MS003` under `.agent/exec_plans/active/gtfs-foundation/`.
- [x] (2026-03-29T23:24:43Z) Completed `MS001` by adding a repository-local Python virtual environment workflow, fixture-based GTFS-static test feeds, a single ingestion entry point, and an automated test loop that proves raw feed loading works.
- [x] (2026-03-30T00:10:38Z) Completed `MS002` by adding normalized GTFS entity models, a separate relationship mapping layer, the `normalized_entities.json` and `relationships.json` artifacts, and fixture-driven tests that prove optional shapes do not break relationship mapping.
- [x] (2026-03-30T04:50:08Z) Completed `MS003` by adding a dedicated validation layer, fixed v1 validation codes, `validation_report.json`, explicit partial-ingestion reporting, fatal artifact suppression for normalized and relationship outputs, and fixture-driven tests for valid, warning-only, invalid, duplicate-id, and unknown-shape scenarios.
- [x] (2026-03-30T19:00:00Z) Defined `MS004` to add an artifact-backed query layer for route, trip, and stop exploration on top of valid or warning-only ingest outputs, with fixed JSON response shapes and explicit artifact-versus-lookup failure contracts.

## Surprises & Discoveries

- Observation: The repository already includes the required planning scaffolding under `.agent/`, but the helper CLI commands referenced by `PLANS.md` are not installed in the current shell session.
  Evidence: `Get-Command agentrules` returned "The term 'agentrules' is not recognized as a name of a cmdlet, function, script file, or executable program."

- Observation: The implementation directories `src/`, `tests/`, `docs/`, and `sample-data/` are present but currently empty, so this first ExecPlan must define both structure and workflow rather than extending existing application code.
  Evidence: Recursive directory listings returned no files inside those directories on 2026-03-29.

- Observation: In this Windows shell, `python` is not usable until a repository-local virtual environment is activated, but the `py` launcher is available globally.
  Evidence: `python --version` failed with a `pyenv` version-selection error, while `py --version` returned `Python 3.14.0`.

- Observation: Pytest's default temp and cache handling triggered sandbox-specific permission errors even though ordinary repository file writes worked.
  Evidence: Initial test runs failed with `PermissionError` under the default temp and cleanup paths. The final run passed after disabling the pytest cache and tmpdir plugins and using deterministic repo-local temporary directories inside the CLI test.

- Observation: The normalized shape count is materially different from the raw `shapes.txt` row count because shapes normalize into shape identifiers, each with an ordered list of shape points.
  Evidence: For `minimal-static-feed`, `feed_summary.json` reports `shapes=2` raw rows, while `normalized_entities.json` reports `shapes=1` normalized shape entity.

- Observation: The original minimal fixture could not satisfy the planned clean-path validation contract because it was missing `calendar_dates.txt`, which MS003 treats as an explicit warning code.
  Evidence: Before adding `sample-data/fixtures/minimal-static-feed/calendar_dates.txt`, validating the minimal fixture produced `MISSING_OPTIONAL_CALENDAR_DATES_FILE` and `valid_with_warnings` instead of `valid`.

## Decision Log

- Decision: Scope the first ExecPlan to GTFS-static ingestion, normalization, relationship mapping, validation, and local developer workflow only.
  Rationale: `AGENTS.md` and the user constraints both prioritize ingestion correctness and relationship accuracy first, and explicitly exclude GTFS-realtime, authentication, multi-user concerns, and deployment work from the initial phase.
  Date/Author: 2026-03-29 / @codex

- Decision: Use a local command-line workflow and fixture feeds as the first observable proof point instead of starting with a web user interface.
  Rationale: A local command is the fastest way to prove GTFS parsing and relationship correctness while keeping parsing logic separate from visualization logic, which is a required architectural guardrail in this repository.
  Date/Author: 2026-03-29 / @codex

- Decision: Treat `shapes.txt` and `calendar_dates.txt` as optional inputs in v1, emit warnings when they are absent, and treat broken foreign-key relationships in required entity chains as validation errors that prevent a feed from being marked fully valid.
  Rationale: GTFS-static feeds are often incomplete in real-world data. This rule balances fail-fast behavior with the repository requirement that partial ingestion may proceed when issues are surfaced clearly and traceably.
  Date/Author: 2026-03-29 / @codex

- Decision: Standardize the Windows 11 PowerShell workflow around `py -m venv .venv`, activation through `.\.venv\Scripts\Activate.ps1`, and then `python -m ...` commands inside the activated environment.
  Rationale: That workflow works in the observed shell, keeps dependencies local to the repository, and avoids relying on a globally configured `python` executable.
  Date/Author: 2026-03-29 / @codex

- Decision: Keep MS001 limited to raw feed loading plus a summary artifact, and defer all validation logic beyond required-file presence and all relationship mapping to later milestones.
  Rationale: The user explicitly limited MS001 to local workflow, fixture strategy, a single ingestion entry point, and the minimum test loop needed to prove ingestion works.
  Date/Author: 2026-03-29 / @codex

- Decision: Split MS002 inspection artifacts into `normalized_entities.json` for normalized entity inspection and `relationships.json` for relationship mappings, while keeping `feed_summary.json` unchanged from MS001.
  Rationale: This preserves the MS001 raw-ingestion contract and keeps normalized entity inspection separate from pure relationship output, which aligns with the repository's modularity and traceability rules.
  Date/Author: 2026-03-29 / @codex

- Decision: Fix the MS003 validation codes to the v1 set named in the implementation plan and make those codes the stable contract for tests and CLI-visible findings.
  Rationale: Stable codes are necessary for traceable automated tests, deterministic artifact parsing, and future UI or API consumers without changing the semantics of a finding.
  Date/Author: 2026-03-29 / @codex

- Decision: Allow normalization and relationship mapping to run in memory before validation completes, but suppress `normalized_entities.json` and `relationships.json` whenever the validation status is `invalid`.
  Rationale: This preserves modular processing and keeps the validator independent of loader internals while enforcing the raw-only partial-ingestion policy on fatal findings.
  Date/Author: 2026-03-29 / @codex

- Decision: Define `source_row` as the 1-based data row number in the source file, excluding the header row, and use `0` only for file-level findings that have no data row.
  Rationale: This keeps row references human-readable and consistent across normalized entities, relationship-derived findings, duplicate detection, and missing-file warnings.
  Date/Author: 2026-03-29 / @codex

- Decision: Sequence consumer-facing work by adding an artifact-backed query layer before visualization data preparation.
  Rationale: The repository is still CLI-first and file-based with no UI framework or persistence, so a stable read-only query contract is the lowest-risk interface for later visualization work.
  Date/Author: 2026-03-30 / @codex

- Decision: Keep MS004 artifact validation minimal and strict by checking only required keys and container shapes, ignoring unknown extra keys, and separating invalid artifact failures from unknown entity lookups.
  Rationale: This preserves forward compatibility for artifact evolution while keeping query failures deterministic and easy to diagnose from the CLI and tests.
  Date/Author: 2026-03-30 / @codex

## Outcomes & Retrospective

The foundation milestones `MS001` through `MS003` are complete. The repository now has a local-first GTFS-static foundation with raw feed loading, normalized GTFS entities, baseline relationship mapping, structured validation findings, fixed severity codes, and explicit partial-ingestion behavior. A valid feed writes all four artifacts, a warning-only feed preserves successful ingestion with surfaced warnings, and an invalid feed exits non-zero while writing only the raw summary and validation report.

`MS004` extends that foundation with the first consumer-facing interface above the validated artifacts: a read-only query layer for route, trip, and stop exploration. The main lesson carried forward is unchanged: raw loading, normalization, relationship mapping, validation, and consumer-facing query access each need their own module boundary so future visualization work stays explainable and testable.

## Context and Orientation

As of 2026-03-29 after completing `MS003`, this repository contains `AGENTS.md`, `PLANS.md`, `.agent/templates/`, a Python project definition in `pyproject.toml`, implementation code under `src/gtfs_visualizer/`, fixture feeds under `sample-data/fixtures/`, and automated tests under `tests/`. There is still no UI or persistence layer, but there are now dedicated modules for raw ingestion, normalized models, relationship mapping, and validation under `src/gtfs_visualizer/`.

This plan uses four plain-language terms consistently. A "GTFS-static feed" means the bundle of text files such as `routes.txt`, `trips.txt`, `stops.txt`, `stop_times.txt`, `calendar.txt`, and optional files like `shapes.txt` and `calendar_dates.txt`. A "normalized model" means an internal representation that stores one source of truth per entity type with stable keys and explicit fields, rather than passing raw tables throughout the codebase. A "relationship graph" means the validated links across those normalized entities, such as which trips belong to which route and which stop times refer to which stop. A "validation report" means a structured list of issues with severity, message, entity references, and whether the feed can proceed to downstream use.

The repository should remain aligned with the stack named in `AGENTS.md`: Python for backend logic, Pandas for initial parsing, SQLAlchemy-compatible data models for future persistence, React plus mapping and graph libraries later for visualization, and PostgreSQL only when persistence becomes necessary. This first ExecPlan deliberately avoids UI-heavy work. It should instead create a backend-first contract that later UI work can depend on without touching the raw parsing layer.

Future contributors should assume that `sample-data/` will hold small, purpose-built fixture feeds that prove correct behavior and broken-edge cases, `src/` will hold implementation modules, `tests/` will hold automated verification, and `docs/` will hold concise local workflow notes only when needed to make the developer loop explicit. No feature in this plan should require cloud services, login flows, or deployment infrastructure.

## Plan of Work

The work now proceeds in four milestones because each milestone produces a new observable capability while minimizing cross-dependencies.

The first milestone establishes the repository's execution contract. It should create the Python project skeleton in `src/`, define a single local entry point for feed ingestion, add minimal fixture feeds under `sample-data/fixtures/`, and add a test command under `tests/` that proves the repository can load a GTFS-static feed from disk. The output at the end of this milestone is not a full relationship engine. It is a reproducible developer workflow with a clear command, a clear test suite, and a clear repository structure for subsequent work.

The second milestone adds the actual domain backbone. It should introduce raw feed loading modules, normalized GTFS entity models, and a relationship-linking layer. The implementation should preserve raw parsed tables separately from normalized entities so the system can trace every downstream relationship back to source data. At the end of this milestone, the project should be able to ingest a valid minimal feed and emit two inspection artifacts: `normalized_entities.json` for normalized entity state and `relationships.json` for baseline relationship mappings that cover routes, trips, stop times, stops, calendar data, and optional shapes when present.

The third milestone adds correctness surfacing. It should formalize validation severity levels, collect relationship problems and file-level problems into a structured report, and make the local ingestion command return clear success, warning, and failure outcomes. This milestone must also define the baseline behavior for partial ingestion so that recoverable issues are preserved and shown rather than silently ignored. No visualization UI should be implemented in this plan. UI specification work may be planned later once the ingestion and relationship contracts are stable.

The fourth milestone adds consumer-facing exploration without introducing a UI framework. It should load valid or warning-only artifact bundles, validate only the minimum required artifact structure, and expose a read-only query interface for routes, route detail, trip detail, and stop detail. Query failures must distinguish invalid or malformed artifact bundles from unknown route, trip, or stop identifiers. The response shapes should be fixed at the top level so later consumers can depend on them.

## Concrete Steps

The implementation agent should work from the repository root `C:\Users\theba\Documents\Vibecoding projects\gtfs-visualizer` and keep all commands repeatable. On Windows 11 PowerShell 7, use the repository-local virtual environment workflow below.

The expected sequence is:

    cd "C:\Users\theba\Documents\Vibecoding projects\gtfs-visualizer"
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -e .[dev]
    python -m pytest tests

The first meaningful automated proof introduced by `MS001` is now in place. `python -m pytest tests` runs a small fixture-driven test suite without requiring external services once the virtual environment is activated.

After `MS001` and `MS002` are implemented, the repository should support a local ingestion command of this form:

    cd "C:\Users\theba\Documents\Vibecoding projects\gtfs-visualizer"
    .\.venv\Scripts\Activate.ps1
    python -m gtfs_visualizer.cli ingest sample-data/fixtures/minimal-static-feed --output-dir .tmp/minimal-report

The expected terminal summary should be short and human-readable, similar to:

    Feed loaded: sample-data\fixtures\minimal-static-feed
    Loaded files: routes.txt, trips.txt, stops.txt, stop_times.txt, calendar.txt, shapes.txt, calendar_dates.txt
    Rows: routes=1, trips=1, stops=2, stop_times=2, calendar=1, shapes=2, calendar_dates=1
    Entities: routes=1, trips=1, stop_times=2, stops=2, services=1, shapes=1
    Relationships: route_to_trips=1, trip_to_stop_times=2, stop_time_to_stops=2, trip_to_shapes=1, service_to_calendar=1
    Optional missing: none
    Validation: 0 errors, 0 warnings
    Output written to .tmp\minimal-report\feed_summary.json

The same command should leave these inspection artifacts in the selected output directory:

    feed_summary.json
    normalized_entities.json
    relationships.json

After `MS003` is implemented, a broken fixture feed should demonstrate surfaced errors:

    cd "C:\Users\theba\Documents\Vibecoding projects\gtfs-visualizer"
    python -m gtfs_visualizer.cli ingest sample-data/fixtures/invalid-relations-feed --output-dir .tmp/invalid-report

The expected terminal summary should make failure explicit, similar to:

    Feed loaded: sample-data\fixtures\invalid-relations-feed
    Loaded files: routes.txt, trips.txt, stops.txt, stop_times.txt, calendar.txt
    Rows: routes=1, trips=1, stops=1, stop_times=2, calendar=1
    Optional missing: shapes.txt, calendar_dates.txt
    Validation: 4 errors, 3 warnings
    Error [UNKNOWN_STOP_ID]: Stop time T1:1 references unknown stop_id STOP_MISSING
    Error [UNKNOWN_TRIP_ID]: Stop time T_UNKNOWN:2 references unknown trip_id T_UNKNOWN
    Error [UNKNOWN_ROUTE_ID]: Trip T1 references unknown route_id R_UNKNOWN
    Error [UNKNOWN_SERVICE_ID]: Trip T1 references unknown service_id WKD_UNKNOWN
    Output written to .tmp\invalid-report\feed_summary.json

## Validation and Acceptance

Acceptance for this ExecPlan is behavior-based rather than code-structure-based. A contributor should be able to run the local ingestion command on a valid minimal GTFS-static fixture and observe all of the following: the command exits successfully, normalized entity counts are reported, the required relationship chains are linked, optional files are handled without crashes, and the expected inspection artifacts are written to disk.

The contributor should also be able to run the same command against a warning-only fixture and an intentionally broken fixture and observe a structured validation result that clearly identifies the finding code, severity, source file, source row, and whether processing continued in a partial state or stopped as invalid. Automated tests in `tests/` should cover clean, warning-only, and invalid feeds. Those tests must prove at least these cases: valid minimal feed, missing optional shapes file, orphan stop reference, unknown trip reference, inconsistent service identifier, duplicate identifier handling, and unknown shape handling.

This plan is complete when three conditions are all true. First, after activating the repository virtual environment, `python -m pytest tests` passes from the repository root. Second, the local ingestion command produces the expected valid, warning-only, and invalid summaries with fixture feeds and the correct artifact suppression behavior on fatal findings. Third, the resulting implementation keeps parsing logic, relationship mapping logic, validation logic, and any future visualization-facing interfaces in separate modules so later UI work does not depend directly on raw feed parsing.

## Idempotence and Recovery

All work in this plan should be additive and safe to repeat. Running the tests repeatedly must not mutate repository state. Running the local ingestion command repeatedly against the same fixture feed should overwrite or refresh only the selected output directory, not modify the source fixture. If an implementation step fails halfway, the contributor should delete only temporary output under `.tmp/` or another explicitly documented scratch directory and rerun the same command.

If a contributor makes a design change while implementing this plan, they must update this document before proceeding so the plan remains the single self-contained source of truth. If a milestone reveals that a command name, module path, or data contract must change, the contributor must update the `Decision Log`, `Progress`, milestone documents, and the registry metadata in the same working session.

## Artifacts and Notes

The required planning artifacts for this ExecPlan live at:

    .agent/exec_plans/active/gtfs-foundation/EP-20260329-001_gtfs-foundation.md
    .agent/exec_plans/active/gtfs-foundation/milestones/archive/MS001_gtfs-foundation.md
    .agent/exec_plans/active/gtfs-foundation/milestones/archive/MS002_gtfs-foundation.md
    .agent/exec_plans/active/gtfs-foundation/milestones/archive/MS003_gtfs-foundation.md

The fixtures that should be introduced during implementation are:

    sample-data/fixtures/minimal-static-feed/
    sample-data/fixtures/missing-shapes-feed/
    sample-data/fixtures/invalid-relations-feed/

These fixture feeds should remain intentionally small so they are easy to inspect by hand. Their purpose is to prove behavior, not to simulate production scale.

## Interfaces and Dependencies

The implementation created by this plan should use Python modules under `src/gtfs_visualizer/`. The exact filenames may be refined during implementation, but the following interfaces must exist by the end of the plan because they define the contract later milestones and later UI work will rely on.

In `src/gtfs_visualizer/cli.py`, define a command-line entry point:

    def main(argv: list[str] | None = None) -> int:
        ...

The `ingest` command exposed by `main` must accept a path to a GTFS-static feed and an output directory for artifacts.

In `src/gtfs_visualizer/ingest/feed_loader.py`, define a loader that reads a directory or extracted feed bundle and preserves raw tabular inputs:

    def load_feed(source_path: Path) -> RawFeedBundle:
        ...

`RawFeedBundle` should contain one raw table per discovered GTFS file and enough source metadata to report filenames and row numbers in validation output.

In `src/gtfs_visualizer/models/normalized.py`, define normalized entities for at least routes, trips, stops, stop times, shapes, services, and the full feed aggregate:

    class NormalizedFeed: ...

Normalization must preserve one source of truth per entity type and must not require the relationship layer to reparse raw tables.

In `src/gtfs_visualizer/relationships/linker.py`, define the baseline relationship contract:

    def build_relationship_graph(feed: NormalizedFeed) -> RelationshipGraph:
        ...

`RelationshipGraph` must expose direct mappings for the required GTFS chains: route to trips, trip to stop times, stop time to stop, trip to shape when present, and service identifier to calendar or calendar date records.

The CLI inspection artifacts should follow this split:

    feed_summary.json            # unchanged raw-ingestion artifact from MS001
    normalized_entities.json    # normalized entity counts and inspectable entity structures
    relationships.json          # relationship mappings plus directly relevant metadata

In `src/gtfs_visualizer/validation/report.py`, define the validation contract:

    class ValidationIssue: ...
    class ValidationReport: ...
    def validate_feed(bundle: RawFeedBundle, feed: NormalizedFeed, graph: RelationshipGraph) -> ValidationReport:
        ...

`ValidationIssue` must record severity, fixed v1 code, message, entity type, entity identifier when available, source filename, and source row reference when known. Severity must distinguish at least `warning` from `error`. `source_row` must be the 1-based data row number in the source file, excluding the header row; use `0` only for file-level findings that have no data row.

The validation artifacts should follow this split:

    validation_report.json      # always written; contains status, summary, partial-ingestion, and findings

When `validation_report.json` reports `status=invalid`, the CLI must still write `feed_summary.json` but must not write `normalized_entities.json` or `relationships.json`.

For dependencies, use Pandas for initial table parsing because `AGENTS.md` names it as the default v1 parsing tool. Design normalized models so they can later map cleanly into SQLAlchemy models, but do not require database setup in this plan. Automated verification should use Python's standard testing flow through `pytest`.

Change note: 2026-03-29. Created the first repository ExecPlan and initial milestone sequence manually because the `agentrules` CLI referenced by `PLANS.md` is not installed in the current environment.
Change note: 2026-03-29. Updated the plan after completing `MS001` to reflect the repository-local virtual environment workflow, the implemented raw-feed loader and CLI, and the archived milestone state.
Change note: 2026-03-29. Updated the plan after completing `MS002` to reflect the normalized model layer, separate relationship layer, new inspection artifact split, passing fixture-driven tests, and the archived milestone state.
Change note: 2026-03-29. Updated the plan after completing `MS003` to reflect the fixed validation-code contract, validation artifact shape, partial raw-only ingestion policy, clean/warning/invalid fixture coverage, and the archived milestone state.
Change note: 2026-03-30. Extended the plan with `MS004` for artifact-backed route, trip, and stop queries with fixed JSON response shapes, minimal artifact validation, and explicit artifact-versus-lookup error handling.
