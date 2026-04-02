---
id: EP-20260401-001
title: "Rename planning workspace path to .agents"
status: done
kind: chore
domain: cross-cutting
owner: "@codex"
created: 2026-04-01
updated: 2026-04-01
tags: ["planning", "migration", "repo-hygiene"]
touches: ["docs", "agents", "tooling"]
risk: low
breaking: false
migration: true
links:
  issue: ""
  pr: ""
  docs: ""
depends_on: []
supersedes: []
---

# Rename planning workspace path to .agents

This ExecPlan is a living document and must be maintained in accordance with PLANS.md.

## Purpose / Big Picture

Standardize planning artifact paths under `.agents/` while preserving short-term compatibility for workflows that still reference the former planning path.

## Progress

- [x] Initial planning created
- [x] Milestones defined
- [x] Milestone implementation completed

## Surprises & Discoveries

- Observation: Pre-change tracked references for the former planning path were concentrated in Markdown and registry JSON.
  Evidence: Baseline inventory on 2026-04-01 found 37 `.md` matches and 7 `.json` matches in tracked files.
- Observation: No tracked runtime Python modules referenced the former planning path.
  Evidence: Baseline grep returned planning/docs artifacts only.

## Decision Log

- Decision: Keep `.agents` as canonical and provide temporary local compatibility via optional filesystem alias instructions.
  Rationale: Avoid long-term dual-path complexity while minimizing disruption for existing local workflows.
  Date/Author: 2026-04-01 / @codex
- Decision: Treat only explicit compatibility guidance files as allowable legacy-path leftovers after cutover.
  Rationale: Enforces deterministic cleanup and prevents silent path drift.
  Date/Author: 2026-04-01 / @codex

## Outcomes & Retrospective

- Planning artifacts were created first, then the directory rename and repository-wide path rewrite were executed.
- Local compatibility support was implemented through setup/removal PowerShell scripts and migration guidance.
- Verification checks passed: tracked legacy-path references are now limited to compatibility artifacts.

## Context and Orientation

Planning artifacts and templates are now rooted at `.agents/` and referenced by `PLANS.md`, `registry.json`, and historical plan artifacts.

## Plan of Work

1. Add migration milestone and baseline inventory.
2. Rename planning artifact directory to `.agents`.
3. Rewrite path references across repository artifacts.
4. Add compatibility instructions and local helper scripts for optional alias setup/removal.
5. Verify no unexpected legacy-path references remain.

## Concrete Steps

    # run legacy-path token grep
    # create EP + milestone artifacts
    # rename planning directory to .agents
    # rewrite references
    # rerun legacy-path token grep
    git grep -n "\.agents"

Expected output:

    legacy-path matches only in explicit compatibility guidance

## Validation and Acceptance

User should be able to:

- Locate planning artifacts under `.agents/exec_plans/...`
- Follow updated documentation paths in `PLANS.md`
- Set up optional local compatibility alias to `.agents` if needed

## Idempotence and Recovery

Migration is largely mechanical text/path replacement. If interrupted, rerun reference inventory and continue until no unexpected legacy-path references remain.

## Artifacts and Notes

- Baseline reference inventory (2026-04-01): `.md` => 37, `.json` => 7
- Temporary legacy-path allowlist after migration:
  - `docs/agent-directory-migration.md`
  - `scripts/setup-agent-compat.ps1`
  - `scripts/remove-agent-compat.ps1`
  - `.gitignore`

## Interfaces and Dependencies

- Public repo path contract moves to `.agents/*`.
- No application runtime API changes expected.
- Depends on Windows PowerShell for optional local junction helper scripts.
