# DevWork data model

## Project

A project is more than a task container. It stores the context needed to understand why work exists.

Suggested fields:

```text
Project
- id
- name
- goal
- specification
- status
- created_at
- updated_at
```

## Stage

A stage represents one implementation step in the project plan.

```text
Stage
- id
- project_id
- title
- description
- position
- status: planned | active | blocked | done
- progress
```

Progress should preferably be derived from tasks rather than manually typed when possible.

## Task

```text
Task
- id
- project_id
- stage_id?
- title
- description?
- status: todo | doing | blocked | done
- priority
- deadline?
- estimate_minutes?
- created_at
- completed_at?
```

A task may belong directly to a project or to one implementation stage.

## Why stage linkage matters

A flat todo list answers "what tasks exist?" but not "what part of the implementation does this move forward?".

Stage linkage enables questions such as:

- which part of the implementation is blocking release?;
- why is this task important?;
- what percentage of stage 3 is complete?;
- which tasks can be postponed without blocking the current stage?;

## Derived views

The storage model should expose projections rather than forcing every UI to rebuild logic independently:

- project progress;
- active stage;
- overdue tasks;
- tasks due today;
- blocked stages;
- unplanned tasks;
- next actionable tasks.

## Future entities

Likely additions:

- `AuditEvent` — immutable mutation history;
- `ActionProposal` — pending confirmation-gated changes;
- `ScheduleBlock` — fixed calendar/work constraints;
- `RecurringTaskRule` — repeated work;
- `ProjectNote` — context that is useful but not part of the technical specification.
