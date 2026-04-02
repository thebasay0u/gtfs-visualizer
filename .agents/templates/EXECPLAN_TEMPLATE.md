---

# 2) `.agents/templates/EXECPLAN_TEMPLATE.md`

```md
---

id: EP-YYYYMMDD-NNN
title: "<Short, action-oriented title>"
status: planned
kind: feature
domain: backend
owner: "@codex"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
touches: []
risk: low
breaking: false
migration: false
links:
issue: ""
pr: ""
docs: ""
depends_on: []
supersedes: []

---

# <ExecPlan Title>

This ExecPlan is a living document and must be maintained in accordance with PLANS.md.

## Purpose / Big Picture

Explain what the user gains after this work and how to verify it.

## Progress

- [ ] Initial planning created
- [ ] Milestones defined
- [ ] First milestone implemented

## Surprises & Discoveries

- Observation:
  Evidence:

## Decision Log

- Decision:
  Rationale:
  Date/Author:

## Outcomes & Retrospective

(To be filled during or after completion)

## Context and Orientation

Describe:

- Current repo structure
- Relevant modules
- GTFS entities involved
- Any assumptions

## Plan of Work

Describe in prose:

- What will be built
- Sequence of changes
- Where code will live

## Concrete Steps

Example:

    cd src
    # run ingestion script

Expected output:

    Loaded GTFS feed successfully

## Validation and Acceptance

User should be able to:

- Upload GTFS feed
- See parsed output
- Verify relationships

## Idempotence and Recovery

Explain how steps can be safely repeated.

## Artifacts and Notes

Include key outputs or logs.

## Interfaces and Dependencies

Define:

- Modules
- Functions
- APIs
- Data structures
