# \# .agent/skills/status\_master.md

# 

# \# Status Master Skill

# 

# Use this skill only at the start of a new Codex thread.

# 

# \## Purpose

# Reconstruct current planning and milestone state from repository artifacts so prompts do not need to restate prior milestones.

# 

# \## Read Order (strict)

# 1\. ./AGENTS.md

# 2\. ./PLANS.md

# 3\. ./.agent/exec\_plans/registry.json

# 4\. ./.agent/exec\_plans/active/\*\*/EP-\*.md

# 5\. ./.agent/exec\_plans/active/\*/milestones/active/\*.md

# 6\. ./.agent/exec\_plans/active/\*/milestones/archive/\*.md

# 

# \## Scope Rules

# \- Only read the files listed above

# \- Do not scan src/, tests/, or unrelated directories

# \- Do not infer state from code; use planning artifacts as source of truth

# 

# \## Responsibilities

# \- Identify:

# &#x20; - active ExecPlan

# &#x20; - completed milestones

# &#x20; - current active/planned milestone

# \- Summarize:

# &#x20; - key completed milestone outcomes relevant to next work

# &#x20; - architectural constraints carried forward

# \- Detect:

# &#x20; - mismatches between ExecPlan, milestone docs, and registry.json

# 

# \## Output

# Produce a concise status snapshot:

# \- active plan

# \- completed milestones

# \- current milestone target

# \- key constraints

# \- any planning artifact drift

# 

# \## Rules

# \- Do not implement anything

# \- Do not modify files

# \- Do not expand scope

# \- Keep output concise and operational

