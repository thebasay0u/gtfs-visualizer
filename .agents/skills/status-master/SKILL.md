---
name: status-master
description: Reconstruct current plan and milestone status from repository planning artifacts at the start of a new Codex thread. Use when you need an operational snapshot of active plan, completed milestones, current target, constraints, and planning drift.
---

# Status Master

Use this skill only at the start of a new Codex thread.

## Purpose

Reconstruct current planning and milestone state from repository artifacts so prompts do not need to restate prior milestones.

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
- Do not infer state from code; use planning artifacts as source of truth.

## Responsibilities

- Identify active ExecPlan, completed milestones, and current active/planned milestone.
- Summarize key completed milestone outcomes relevant to next work.
- Summarize architectural constraints carried forward.
- Detect mismatches between ExecPlan, milestone docs, and `registry.json`.

## Output

Produce a concise status snapshot:

- Active plan
- Completed milestones
- Current milestone target
- Key constraints
- Any planning artifact drift

## Rules

- Do not implement anything.
- Do not modify files.
- Do not expand scope.
- Keep output concise and operational.