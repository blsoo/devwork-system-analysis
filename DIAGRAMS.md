# DevWork diagrams

This page turns the project into a compact system-analysis case study. The diagrams describe the public-safe architecture and domain model; they do not depend on private infrastructure.

## 1. System context

```mermaid
flowchart LR
    U[User] --> UI[Telegram / CLI / Web adapter]
    UI --> IR[Intent Router]
    IR --> Q[Read-only Query Service]
    IR --> AP[Action Proposal Service]
    AP --> C[Explicit Confirmation]
    C --> CS[Command Service]
    Q --> DB[(PostgreSQL)]
    CS --> DB
    CS --> AE[Audit Event]
    DP[Daily Planner] --> DB
    DB --> DP
```

The key boundary is between understanding a request and receiving permission to mutate state.

## 2. Core ER model

```mermaid
erDiagram
    PROJECT ||--o{ STAGE : contains
    PROJECT ||--o{ TASK : owns
    STAGE ||--o{ TASK : groups
    PROJECT ||--o{ ACTION_PROPOSAL : receives
    ACTION_PROPOSAL ||--o| AUDIT_EVENT : produces

    PROJECT {
        bigint id PK
        string name
        text goal
        text specification
        string status
        timestamp created_at
        timestamp updated_at
    }

    STAGE {
        bigint id PK
        bigint project_id FK
        string title
        int position
        string status
        int progress
    }

    TASK {
        bigint id PK
        bigint project_id FK
        bigint stage_id FK
        string title
        string status
        int priority
        timestamp deadline
        int estimate_minutes
    }

    ACTION_PROPOSAL {
        bigint id PK
        bigint project_id FK
        string action_type
        json payload
        string status
        timestamp expires_at
    }

    AUDIT_EVENT {
        bigint id PK
        string event_type
        bigint entity_id
        json payload
        timestamp created_at
    }
```

## 3. Read vs write decision flow

```mermaid
flowchart TD
    A[User message] --> B{Intent recognized?}
    B -- No --> X[Return unsupported / clarification]
    B -- Yes --> C{Read-only?}
    C -- Yes --> D[Execute query]
    D --> E[Return result]
    C -- No --> F[Build action proposal]
    F --> G[Show exact planned change]
    G --> H{Confirmed?}
    H -- No --> I[Cancel / expire]
    H -- Yes --> J[Execute command]
    J --> K[Persist state]
    K --> L[Write audit event]
    L --> M[Return result]
```

## 4. Mutation sequence

```mermaid
sequenceDiagram
    actor User
    participant Adapter
    participant Router as Intent Router
    participant Proposal as Action Proposal
    participant Command as Command Service
    participant DB as PostgreSQL
    participant Audit as Audit Log

    User->>Adapter: "close task 17"
    Adapter->>Router: parse(text)
    Router-->>Adapter: COMPLETE_TASK(17)
    Adapter->>Proposal: create proposal
    Proposal-->>User: preview exact mutation
    User->>Adapter: confirm
    Adapter->>Command: execute(proposal_id)
    Command->>DB: update task 17
    DB-->>Command: committed
    Command->>Audit: append immutable event
    Command-->>User: task completed
```

## 5. Task lifecycle

```mermaid
stateDiagram-v2
    [*] --> todo
    todo --> doing: start
    todo --> blocked: block
    doing --> blocked: dependency/problem
    blocked --> todo: unblock
    blocked --> doing: resume
    doing --> done: complete
    todo --> done: complete directly
    done --> [*]
```

## 6. Daily planner flow

```mermaid
flowchart TD
    A[(Tasks)] --> B[Exclude done / blocked]
    B --> C[Calculate transparent score]
    C --> C1[Priority]
    C --> C2[Overdue state]
    C --> C3[Deadline proximity]
    C --> C4[Already doing]
    C1 --> D[Rank actionable tasks]
    C2 --> D
    C3 --> D
    C4 --> D
    D --> E[Daily Plan]
    E --> F[Explain why each task is ranked]
```

## 7. Project execution model

```mermaid
flowchart LR
    G[Goal] --> S[Specification]
    S --> P[Implementation Plan]
    P --> ST[Stages]
    ST --> T[Tasks]
    T --> DL[Deadlines / Priority]
    DL --> DP[Daily Plan]
    T --> PR[Derived Progress]
    ST --> PR
```

## Interview talking points

These diagrams make it possible to discuss the project without hiding behind code:

- why `project_id` and `stage_id` are foreign keys;
- why a task may exist without a stage;
- why confirmation is a separate domain entity;
- how idempotent confirmation should behave;
- which state transitions are allowed;
- why the planner is deterministic before adding ML/LLM logic;
- where REST/Telegram/CLI adapters end and application logic begins.
