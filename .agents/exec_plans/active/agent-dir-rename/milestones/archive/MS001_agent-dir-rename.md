---
id: EP-20260401-001/MS001
execplan_id: EP-20260401-001
ms: 1
title: "Execute planning path migration to .agents with compatibility guidance"
status: done
domain: cross-cutting
owner: "@codex"
created: 2026-04-01
updated: 2026-04-01
tags: ["migration", "docs", "tooling"]
risk: low
links:
  issue: ""
  docs: ""
  pr: ""
---

# Execute planning path migration to .agents with compatibility guidance

## Objective

Complete the repository-wide migration to `.agents`, then leave only explicit temporary compatibility guidance for legacy local workflows.

## Definition of Done

- [x] Directory renamed to `.agents`
- [x] Repository references updated to `.agents`
- [x] Compatibility setup/removal guidance added
- [x] Verification confirms no unexpected legacy-path references in tracked files beyond the compatibility allowlist

## Scope

### In Scope

- Planning artifacts under the former planning-path tree
- PLANS docs and templates
- Registry path fields
- Historical repository artifacts that still referenced the former planning path
- Compatibility scripts and migration note

### Out of Scope

- Runtime application behavior changes
- Permanent dual-path support

## Workstreams & Tasks

- Workstream A: Create migration artifacts and baseline inventory.
- Workstream B: Execute path rename and mechanical text replacement.
- Workstream C: Add compatibility guidance and cleanup criteria.
- Workstream D: Run static verification for expected leftover references only.

## Risks & Mitigations

- Risk: Missed string references break planning workflows.
  Mitigation: Search-driven replacement with explicit no-residual-reference gate.
- Risk: Compatibility mechanism becomes permanent.
  Mitigation: Document strict removal criteria and follow-up milestone requirement.

## Validation / QA Plan

    # run legacy-path token grep
    git grep -n "\.agents"

Expected:
- `.agents` appears in planning artifacts/docs/registry paths.
- Legacy-path token appears only in compatibility guidance content.

## Changelog

- 2026-04-01: Milestone created.
- 2026-04-01: Migration executed, validated, and archived.
