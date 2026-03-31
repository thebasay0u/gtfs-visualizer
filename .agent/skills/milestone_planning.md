# \# .agent/skills/milestone\_planning.md

# 

# \# Milestone Planning Skill

# 

# Use this skill for plan-mode runs only.

# 

# \## Purpose

# Produce a strict, scoped milestone plan with no implementation.

# 

# \## Read Order (strict)

# 1\. ./AGENTS.md

# 2\. ./PLANS.md

# 3\. ./.agent/exec\_plans/registry.json

# 4\. ./.agent/exec\_plans/active/\*\*/EP-\*.md

# 5\. ./.agent/exec\_plans/active/\*/milestones/active/\*.md

# 

# \## Scope Rules

# \- Do not scan src/, tests/, or unrelated directories unless explicitly required

# \- Focus only on planning artifacts and current milestone context

# 

# \## Core Rules

# \- Follow AGENTS.md and PLANS.md strictly

# \- Plan only — do not implement

# \- Do not generate placeholder code

# \- Do not expand beyond the named milestone

# \- Preserve existing layer boundaries unless explicitly changed by scope

# \- Keep outputs deterministic and minimal

# 

# \## Required Plan Contents

# \- exact scope definition

# \- files/modules to create or modify

# \- artifact/input/output changes

# \- service and loader boundaries

# \- CLI scope (if applicable)

# \- error model (if applicable)

# \- acceptance criteria

# \- test strategy

# \- risks / assumptions

# \- brief milestone summary

# 

# \## Process Requirement

# \- Apply Plan Hygiene Skill before producing the plan

# 

# \## Stop Condition

# \- Stop after producing the milestone plan and summary

