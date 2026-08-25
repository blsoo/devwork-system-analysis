# DevWork — requirements specification

This document turns the DevWork concept into a small, reviewable set of functional and non-functional requirements. It is intentionally scoped to the public portfolio prototype.

## 1. Purpose

DevWork helps a user keep project intent and execution connected:

`Goal -> Specification -> Implementation Plan -> Stages -> Tasks -> Daily Plan`

The public prototype focuses on deterministic task operations, safe mutations and explainable daily planning.

## 2. Actors

- **User** — views project state and requests actions.
- **Client adapter** — Telegram, CLI or future HTTP UI that translates user interaction into application requests.
- **DevWork application** — validates requests, applies business rules and writes audit events.

## 3. Functional requirements

### FR-01 — Project structure

The system shall represent a project with a goal, specification, ordered implementation stages and tasks.

**Acceptance criteria**

- every stage belongs to one project;
- a task belongs to one project;
- a task may optionally belong to a stage;
- project/stage/task identifiers are stable and unique inside their entity type.

### FR-02 — Read project tasks

The system shall allow a user to retrieve tasks for a project.

**Acceptance criteria**

- results may be filtered by status;
- a read operation does not create an action proposal;
- a read operation does not mutate task state.

### FR-03 — Distinguish reads from mutations

The system shall classify supported user intents as read-only or mutating before execution.

**Acceptance criteria**

- `show_tasks` is read-only;
- `complete_task` is mutating;
- unsupported text is not silently converted into a mutation.

### FR-04 — Mutation proposal

A mutating request shall create an action proposal before any real state change occurs.

**Acceptance criteria**

- the proposal stores the intended action and target entity;
- the proposal includes a human-readable preview;
- creating a proposal does not change the target task;
- an invalid target is rejected.

### FR-05 — Explicit confirmation

The system shall require explicit confirmation before applying a pending mutation proposal.

**Acceptance criteria**

- only a valid pending proposal can be confirmed;
- confirmation applies the exact stored proposal;
- changing the target/action requires a new proposal;
- expired or stale proposals are rejected.

### FR-06 — Idempotent repeated confirmation

Repeated confirmation of the same already-applied proposal shall not apply the mutation twice.

**Acceptance criteria**

- the first valid confirmation applies the mutation once;
- subsequent confirmations return the already-applied outcome or equivalent stable result;
- no duplicate state transition is produced.

### FR-07 — Explainable daily plan

The system shall produce a deterministic daily task ranking from transparent inputs.

**Acceptance criteria**

- completed tasks are excluded;
- blocked tasks are excluded;
- ranking may consider priority, deadline distance, overdue state and already-started work;
- every selected task includes at least one ranking reason.

### FR-08 — Audit mutation outcome

A successful mutation shall produce an audit event describing what changed.

**Acceptance criteria**

- the event identifies the action type and target entity;
- the event is written only after a successful mutation;
- repeated idempotent confirmation does not create duplicate business mutations.

### FR-09 — Fail safely on ambiguous input

The system shall not guess a destructive action when the request cannot be mapped to a supported mutation with sufficient confidence.

**Acceptance criteria**

- unsupported text produces an `unknown`/unsupported result;
- no database mutation is performed;
- no hidden fallback converts free text into a write.

## 4. Non-functional requirements

### NFR-01 — Safety

State-changing operations must use the same confirmation rule regardless of client adapter.

### NFR-02 — Determinism

Given the same stored state and planning inputs, the baseline daily planner should produce the same ranking.

### NFR-03 — Explainability

Important automated decisions should expose a reason that can be shown to a user or reviewer.

### NFR-04 — Separation of concerns

Telegram/CLI/HTTP adapters must not contain the core mutation rules. Business rules belong in the application layer.

### NFR-05 — Auditability

The system should preserve enough mutation history to answer: who/what requested a change, what was applied and when.

### NFR-06 — Portability

The core public prototype should run without a paid external AI API and without depending on a specific chat platform.

## 5. Out of scope for the public prototype

- unrestricted LLM writes to storage;
- calendar synchronization;
- multi-user permissions;
- production authentication/authorization;
- distributed queues;
- autonomous changes without confirmation.
