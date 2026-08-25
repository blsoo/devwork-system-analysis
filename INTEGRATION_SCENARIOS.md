# DevWork integration scenarios

This document describes public-safe integration scenarios for the DevWork portfolio. It focuses on contracts, state transitions and failure handling rather than infrastructure details.

## Scenario 1 — Read project state

**Goal:** return the current project context without changing state.

```mermaid
sequenceDiagram
    actor User
    participant Client
    participant API
    participant QueryService
    participant DB as PostgreSQL

    User->>Client: Open project
    Client->>API: GET /projects/{id}
    API->>QueryService: getProject(id)
    QueryService->>DB: SELECT project + derived progress
    DB-->>QueryService: project state
    QueryService-->>API: DTO
    API-->>Client: 200 JSON
    Client-->>User: Project summary
```

Expected properties:

- operation is read-only;
- missing project returns `404`;
- response exposes derived state rather than asking the client to reconstruct business rules;
- no audit mutation event is created.

## Scenario 2 — Complete a task through confirmation

**Goal:** change a task only after the user sees and confirms the exact proposed mutation.

```mermaid
sequenceDiagram
    actor User
    participant Client
    participant API
    participant ProposalService
    participant CommandService
    participant DB as PostgreSQL
    participant Audit

    User->>Client: Complete task 17
    Client->>API: POST /actions/proposals
    API->>ProposalService: create(COMPLETE_TASK, task=17)
    ProposalService->>DB: validate task + save pending proposal
    DB-->>ProposalService: proposal id
    ProposalService-->>Client: preview + expires_at
    Client-->>User: Show exact planned change
    User->>Client: Confirm
    Client->>API: POST /actions/proposals/{id}/confirm
    API->>CommandService: confirm(id)
    CommandService->>DB: transaction: lock proposal + update task
    DB-->>CommandService: committed
    CommandService->>Audit: append event
    CommandService-->>Client: success
```

Expected properties:

- proposal creation has no task side effect;
- confirmation applies the stored proposal, not arbitrary new client payload;
- expired/stale proposal fails closed;
- repeated confirmation is idempotent;
- mutation and audit event belong to one logical operation.

## Scenario 3 — Duplicate confirmation

A client may retry after a timeout even though the first request succeeded.

```mermaid
flowchart TD
    A[Confirm request] --> B{Proposal state}
    B -- pending --> C[Apply mutation]
    C --> D[Mark confirmed]
    D --> E[Return success]
    B -- already confirmed --> F[Return same logical success]
    B -- expired/cancelled --> G[Reject without mutation]
```

The important requirement is not "never receive duplicates". The requirement is that duplicate delivery must not duplicate the business effect.

## Scenario 4 — Daily plan generation

```mermaid
sequenceDiagram
    actor User
    participant Client
    participant API
    participant Planner
    participant DB as PostgreSQL

    User->>Client: Show today's plan
    Client->>API: GET /projects/{id}/today
    API->>Planner: buildPlan(projectId)
    Planner->>DB: load actionable tasks
    DB-->>Planner: tasks
    Planner->>Planner: exclude blocked/done
    Planner->>Planner: score priority/deadline/overdue/doing
    Planner-->>API: ranked items + reasons
    API-->>Client: 200 JSON
```

The planner is deterministic in the first version so its result can be explained and tested.

## Scenario 5 — Concurrent stale action

Two clients may act on the same task state.

Example:

1. client A creates a proposal to complete task 17;
2. client B completes task 17 through another valid action;
3. client A confirms its old proposal.

Expected behaviour:

- confirmation re-validates the domain state;
- if the proposal no longer represents a valid transition, return `409 Conflict`;
- do not silently apply an outdated operation;
- record only the mutation that actually changes state.

## Integration questions an interviewer can ask

- Why separate proposal creation from confirmation?
- Where should idempotency be enforced?
- What makes a stale proposal different from an invalid JSON request?
- Why use `409` for an invalid current-state transition?
- What should happen if the database commit succeeds but the client times out?
- Which operations need transactions?
- Why should clients not own business-rule reconstruction?
