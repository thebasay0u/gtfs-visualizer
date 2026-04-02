---
name: milestone-planning
description: Create strict, scoped milestone plans for this GTFS Visualizer repository without implementation changes. Use when planning a specific milestone and you need exact scope, acceptance criteria, test strategy, risks, assumptions, and planning-artifact synchronization.
---

# Milestone Planning

Use this skill for plan-mode work only.

## Purpose

Produce a strict, scoped milestone plan with no implementation.

## Read Order (strict)

1. `./AGENTS.md`
2. `./PLANS.md`
3. `./.agents/exec_plans/registry.json`
4. `./.agents/exec_plans/active/**/EP-*.md`
5. `./.agents/exec_plans/active/*/milestones/active/*.md`

## Scope Rules

- Do not scan `src/`, `tests/`, or unrelated directories unless explicitly required.
- Focus only on planning artifacts and current milestone context.

## Core Rules

- Follow `AGENTS.md` and `PLANS.md` strictly.
- Plan only; do not implement.
- Do not generate placeholder code.
- Do not expand beyond the named milestone.
- Preserve existing layer boundaries unless explicitly changed by scope.
- Keep outputs deterministic and minimal.

## Required Plan Contents

- Exact scope definition
- Files/modules to create or modify
- Artifact/input/output changes
- Service and loader boundaries
- CLI scope (if applicable)
- Error model (if applicable)
- Acceptance criteria
- Test strategy
- Risks and assumptions
- Brief milestone summary

## Process Requirement

Apply `$plan-hygiene` before producing the plan.

## Stop Condition

Stop after producing the milestone plan and summary.