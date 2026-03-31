# .agent/skills/plan\_hygiene.md

# Plan Hygiene Skill

Use this skill at the start of every planning or implementation run.

## Purpose

Ensure planning artifacts (ExecPlan, milestones, registry) are synchronized with actual project state.

## Read Order (strict)

1. ./AGENTS.md
2. ./PLANS.md
3. ./.agent/exec_plans/registry.json
4. ./.agent/exec_plans/active/**/EP-*.md
5. ./.agent/exec_plans/active/*/milestones/active/*.md
6. ./.agent/exec_plans/active/*/milestones/archive/*.md

## Scope Rules

* Only read the files listed above
* Do not scan src/, tests/, or unrelated directories

## Required Checks (Before Work)

* Active ExecPlan reflects actual completed milestones
* Completed milestones are archived (not left active)
* Active milestone doc matches intended current milestone
* registry.json matches actual milestone state

## If Mismatch Found

* Include reconciliation as part of the current milestone plan
* Record mismatch in:

  * Progress
  * Decision Log
  * or milestone notes

## Required Updates (During Planning)

* Ensure:

  * current milestone doc exists and is marked active
  * prior milestones are properly archived
  * registry.json reflects correct milestone state

## Required Updates (After Implementation)

* Update ExecPlan:

  * Progress
  * Decision Log
  * Outcomes / Retrospective
* Archive completed milestone doc
* Activate or define next milestone if applicable
* Update registry.json

## Rule

Planning artifact reconciliation is part of the milestone deliverable, not optional.

