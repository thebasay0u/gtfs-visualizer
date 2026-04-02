---
name: plan-hygiene
description: Reconcile planning artifacts (ExecPlan, milestone files, registry.json) with actual project state before and after work. Use at the start of planning or implementation runs to detect and fix drift in planning metadata and milestone status.
---

# Plan Hygiene

Use this skill at the start of every planning or implementation run.

## Purpose

Ensure planning artifacts (ExecPlan, milestones, registry) are synchronized with actual project state.

## Read Order (strict)

1. `./AGENTS.md`
2. `./PLANS.md`
3. `./.agents/exec_plans/registry.json`
4. `./.agents/exec_plans/active/**/EP-*.md`
5. `./.agents/exec_plans/active/*/milestones/active/*.md`
6. `./.agents/exec_plans/active/*/milestones/archive/*.md`

## Scope Rules

- Only read the files listed above.
- Do not scan `src/`, `tests/`, or unrelated directories.

## Required Checks (Before Work)

- Active ExecPlan reflects actually completed milestones.
- Completed milestones are archived (not left active).
- Active milestone doc matches intended current milestone.
- `registry.json` matches actual milestone state.

## If Mismatch Found

- Include reconciliation as part of the current milestone plan.
- Record mismatch in Progress, Decision Log, or milestone notes.

## Required Updates (During Planning)

- Ensure current milestone doc exists and is marked active.
- Ensure prior milestones are properly archived.
- Ensure `registry.json` reflects correct milestone state.

## Required Updates (After Implementation)

- Update ExecPlan: Progress, Decision Log, Outcomes/Retrospective.
- Archive completed milestone doc.
- Activate or define next milestone when applicable.
- Update `registry.json`.

## Rule

Planning artifact reconciliation is part of the milestone deliverable, not optional.