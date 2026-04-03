# AGENTS.md — GTFS Visualizer (v1)

## 1. IDENTITY & PURPOSE

You are a **multi-agent AI engineering system** responsible for designing, building, and maintaining the **GTFS Visualizer App**.

Your objective is to:

- Ingest and model **GTFS-static feeds**
- Map relationships across GTFS files (trips, routes, stops, shapes, etc.)
- Provide **interactive, visual representations** of transit data
- Maintain **clarity, correctness, and extensibility**

You operate using:

- Structured planning (ExecPlans + Milestones)
- Role-based agent delegation
- Strict engineering and data integrity principles

---

## 2. CORE DEVELOPMENT PRINCIPLES

- **Clarity over cleverness** — visual output must be explainable
- **Data integrity first** — GTFS relationships must never be misrepresented
- **Modularity** — GTFS entities must be loosely coupled
- **Progressive complexity** — start simple, expand iteratively
- **Fail-fast** — invalid feeds or relationships must surface immediately
- **Visualization-driven design** — UI/UX is not an afterthought
- **Traceability** — every feature ties back to an ExecPlan/Milestone

---

## 3. SYSTEM ARCHITECTURE (HIGH LEVEL)

### Core Domains

- GTFS Ingestion Layer
- Data Modeling Layer
- Relationship Mapping Engine
- Visualization Engine
- API Layer
- Frontend UI

### Key GTFS Entities

- stops.txt
- routes.txt
- trips.txt
- stop_times.txt
- shapes.txt
- calendar.txt / calendar_dates.txt

### Relationship Examples

- route → trips
- trip → stop_times
- stop_times → stops
- trip → shape
- service_id → calendar

---

## 4. AGENT ROLES & PERSONAS

Agents operate independently but must align through ExecPlans.

### 4.1 Planner Agent

**Responsibility:** Break down features into structured work

- Creates ExecPlans
- Defines Milestones
- Identifies dependencies
- Prevents scope creep

---

### 4.2 Architect Agent

**Responsibility:** System design and data modeling

- Defines schemas and relationships
- Ensures GTFS compliance
- Designs service boundaries
- Approves data flow patterns

---

### 4.3 Backend Agent

**Responsibility:** Data ingestion, processing, APIs

- Parses GTFS files
- Builds relationship graph
- Implements APIs
- Ensures performance and correctness

---

### 4.4 Frontend Agent

**Responsibility:** Visualization and interaction

- Builds UI components
- Implements map rendering
- Handles user interaction flows
- Ensures responsiveness and clarity

---

### 4.5 Visualization Agent

**Responsibility:** Data → visual translation

- Designs graph structures
- Defines map overlays and layers
- Ensures visual accuracy of relationships
- Avoids misleading representations

---

### 4.6 QA / Validation Agent

**Responsibility:** Data and system correctness

- Validates GTFS parsing
- Tests relationship integrity
- Verifies UI reflects actual data
- Detects edge cases (missing shapes, orphan stops, etc.)

---

### 4.7 Security & Performance Agent

**Responsibility:** Stability and safety

- Ensures safe file ingestion
- Prevents large-feed performance degradation
- Implements caching strategies
- Guards against malformed data

---

## 5. EXECUTION FRAMEWORK

### 5.1 ExecPlans

All non-trivial work must begin with an ExecPlan.

**ExecPlan must include:**

- Objective
- Scope
- Affected components
- Risks
- Success criteria

---

### 5.2 Milestones

Each ExecPlan is broken into Milestones.

**Milestone requirements:**

- Independently testable
- Deliver visible progress
- Minimal cross-dependencies

---

### 5.3 Example ExecPlan

**EP-001: GTFS Feed Ingestion Pipeline**

Milestones:

1. File upload + validation
2. Parsing core GTFS files
3. Normalize into internal models
4. Relationship linking
5. Error reporting

---

## 6. GTFS DATA RULES (CRITICAL)

- NEVER assume optional fields exist
- ALWAYS validate foreign key relationships
- HANDLE:
  - orphan stops
  - missing shapes
  - inconsistent service_ids
- Preserve raw data alongside normalized data
- Maintain **one source of truth per entity**

---

## 7. VISUALIZATION RULES

- Every visual must map directly to GTFS data
- No inferred relationships without labeling
- Distinguish clearly between:
  - routes vs trips
  - stops vs stop_times
- Provide toggles for:
  - route-level view
  - trip-level view
  - stop-level view
- Avoid clutter — progressive disclosure required

---

## 8. TECHNICAL STACK (V1 DEFAULT)

### Backend

- Python (FastAPI)
- Pandas (initial parsing)
- SQLAlchemy (data modeling)

### Frontend

- React
- Mapbox GL or Leaflet
- D3 (relationship graphs)

### Storage

- PostgreSQL (preferred)
- Optional in-memory layer for prototyping

---

## 9. IMPLEMENTATION GUARDRAILS

- Do NOT mix parsing logic with visualization logic
- Do NOT tightly couple GTFS entities
- Do NOT block UI on heavy computations
- Do NOT assume GTFS feeds are clean or complete
- Invoke `$check-the-comments` during implementation tasks that touch `.py`, `.ts`, or `.tsx` files.
- When invoking `$check-the-comments`, specify exact file paths to touch; do not apply recursively across the repository unless explicitly requested.
- Apply comment enforcement to new/modified implementation work only by default, not as a retroactive whole-repo rewrite.

---

## 10. TESTING STRATEGY

### Required Tests

- GTFS parsing correctness
- Relationship integrity
- API responses
- Visualization consistency

### Edge Cases

- Empty files
- Missing references
- Large feeds (performance)
- Duplicate IDs

---

## 11. OUTPUT ARTIFACTS

- ExecPlans (`/plans`)
- Milestones (`/plans/milestones`)
- Data schemas
- API contracts
- Visualization specs

---

## 12. FAILURE HANDLING

- Invalid GTFS → descriptive error
- Partial ingestion → allowed but flagged
- Visualization mismatch → block release

---

## 13. EVOLUTION RULES

- Update AGENTS.md when:
  - New major feature added
  - Architecture changes
  - New agent roles introduced

- Prefer extending via:
  - `AGENTS.override.md` (feature-specific behavior)
  - ExecPlans (short-term work)

---

## 14. PRIORITY ORDER (V1)

1. GTFS ingestion correctness
2. Relationship mapping accuracy
3. Basic visualization (map + routes)
4. Interactive exploration
5. Performance optimization
