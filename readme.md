# Care Circles — Hackathon Specification (FastAPI + CrewAI + Supabase)

## Purpose

Care Circles is an AI-assisted coordination system designed to transform an unstructured caregiving request into a clear, actionable, and human-approved care plan. The system ingests a narrative description of a caregiving situation, analyzes needs and constraints, generates coordinated tasks, and publishes them for helpers after explicit human approval.

This document defines the **implementation specification** for a one-week hackathon build. It is the authoritative description of system behavior, architecture, data flow, and agent responsibilities.

---

## High-Level Architecture

The system consists of three primary components:

1. **Web Application**
   - User interface for organizers and helpers
   - Authenticated via Supabase Auth
   - Communicates exclusively with the backend API

2. **Backend API (Python / FastAPI)**
   - Central orchestration layer
   - Exposes REST endpoints for all system operations
   - Executes CrewAI agents
   - Manages background jobs
   - Persists all data in Supabase

3. **Supabase**
   - Authentication (users, sessions, access control)
   - Primary database (Postgres)
   - Source of truth for all domain entities

---

## Execution Model

### Asynchronous Agent Execution

Agent execution is handled asynchronously using an internal job runner within the FastAPI service.

1. The API receives a Care Request from the web application.
2. The request is persisted immediately.
3. A background job is enqueued and executed by the API server.
4. The job runs the CrewAI agent pipeline (A1–A5).
5. Intermediate and final artifacts are persisted to Supabase.
6. The web application polls job status and retrieves results when ready.

This model provides responsiveness, traceability, and simplicity while preserving a production-style flow.

---

## Core Domain Entities

### User
- Authenticated via Supabase Auth
- Roles: organizer, helper (role-based behavior is enforced at the API layer)

### CareCircle
Represents a coordination group.

Fields:
- id
- name
- description
- created_by
- created_at

---

### CareRequest
Represents the initial caregiving narrative.

Fields:
- id
- care_circle_id
- narrative
- constraints
- boundaries
- status (submitted, processing, completed)
- created_at

---

### NeedsMap
Structured interpretation of the CareRequest.

Fields:
- id
- care_request_id
- summary
- identified_needs (JSON)
- risks (JSON)
- assumptions
- created_at

---

### CareTask
Actionable unit of work.

Fields:
- id
- care_circle_id
- care_request_id
- title
- description
- category
- priority
- status (draft, active, completed)
- created_at

---

### ReviewPacket
Human approval artifact.

Fields:
- id
- care_request_id
- summary
- draft_tasks (JSON)
- agent_notes
- approval_status (pending, approved)
- created_at

---

### Job
Tracks background execution.

Fields:
- id
- care_request_id
- status (queued, running, completed, failed)
- started_at
- completed_at
- error (nullable)

---

## Agent Pipeline Specification (CrewAI)

The system executes a deterministic, ordered agent pipeline.

### A1 — Intake & Needs Analysis
**Input:** CareRequest  
**Output:** NeedsMap  

Responsibilities:
- Interpret the caregiving narrative
- Extract explicit and implicit needs
- Identify constraints and sensitivities
- Produce a structured NeedsMap

---

### A2 — Task Generation
**Input:** NeedsMap  
**Output:** Draft CareTasks  

Responsibilities:
- Generate actionable, human-friendly tasks
- Assign priority and category
- Maintain respectful and supportive tone
- Avoid assumptions beyond provided context

---

### A3 — Guardian & Quality Pass
**Input:** Draft CareTasks  
**Output:** Revised CareTasks + Notes  

Responsibilities:
- Enforce boundaries and constraints
- Remove or soften sensitive language
- Flag potential risks or ambiguities
- Ensure tasks are safe and appropriate

---

### A4 — Optimization (Optional Enhancement)
**Input:** Revised CareTasks  
**Output:** Optimized CareTasks  

Responsibilities:
- Detect duplication
- Improve coverage and clarity
- Adjust task granularity

---

### A5 — Review Packet Assembly
**Input:** Finalized Draft Tasks + Notes  
**Output:** ReviewPacket  

Responsibilities:
- Summarize the plan
- Present tasks for human review
- Provide agent rationale and context

---

## Human-in-the-Loop Approval

No task becomes active without explicit human approval.

Approval Flow:
1. Organizer retrieves the ReviewPacket.
2. Organizer may edit, remove, or approve tasks.
3. Upon approval, tasks transition from `draft` to `active`.
4. Approved tasks become visible to helpers.

This gate is a first-class system invariant.

---

## API Surface (Specification)

### Core Endpoints

- `POST /care-circles`
- `GET /care-circles/{id}`

- `POST /care-requests`
- `GET /care-requests/{id}`

- `GET /jobs/{id}`

- `GET /review-packets/{id}`
- `POST /review-packets/{id}/approve`

- `GET /care-circles/{id}/tasks`

All endpoints require Supabase-authenticated requests.

---

## Persistence Model

- Supabase Postgres is the sole persistence layer.
- JSON-capable columns are used for agent outputs to maximize iteration speed.
- All agent artifacts are persisted for traceability.

---

## Observability & Traceability

Each CareRequest execution captures:
- Job lifecycle timestamps
- Agent outputs
- Approval decisions

This enables:
- Debugging
- Demo replay
- Future evaluation

---

## Expected Hackathon Outcome

At completion, the system supports:
- Authenticated users
- Creation of care circles
- Submission of caregiving narratives
- AI-generated, reviewable care plans
- Human-approved task publication
- Clear end-to-end demonstration of value

---

## Design Principles

- Human-first
- Explicit approval
- Clear artifacts
- Simple infrastructure
- Extensible agent design

---

This specification defines the Care Circles hackathon implementation.
