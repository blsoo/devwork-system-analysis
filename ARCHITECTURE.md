# DevWork architecture

## Design goals

DevWork should be useful as a deterministic project manager even when no external LLM is available.

The system therefore separates four responsibilities:

1. **Adapters** receive input from Telegram, CLI or a future web UI.
2. **Intent routing** maps supported user language to known application intents.
3. **Application services** enforce project/task rules.
4. **Storage** persists state through a replaceable repository interface.

An optional conversational assistant can sit beside this path, but it must not silently bypass it.

## Request classes

### Read-only

Examples:

- show today's tasks;
- show project progress;
- what is overdue?;
- which implementation stage is active?;
- what should I work on next?

These may execute immediately.

### Mutating

Examples:

- create task;
- close task;
- move deadline;
- change stage status;
- edit project specification.

The router may understand the request, but execution is split into two phases:

```text
request -> parsed intent -> action preview -> confirmation -> mutation
```

A short-lived action token can bind confirmation to the exact proposed change.

## Application boundary

The Telegram handler should not contain logic such as deadline scoring, progress calculation or task state transitions.

Instead:

```text
TelegramUpdate
    -> TelegramAdapter
    -> IntentRouter
    -> QueryService / CommandService
    -> Repository
```

This makes the same business logic reusable from tests, CLI and future HTTP endpoints.

## AI boundary

The conversational layer receives a read-only context projection, for example:

```json
{
  "project": "DevWork",
  "goal": "project/work automation assistant",
  "active_stage": "deterministic command layer",
  "overdue_tasks": 1,
  "today": ["add confirmation flow", "write router tests"]
}
```

It may explain, summarize or suggest.

If the user asks it to change real data, the response must be converted into a supported deterministic action and pass through the normal confirmation flow.

## Failure behaviour

DevWork should prefer explicit failure over ambiguous state changes.

Examples:

- unknown task id -> reject;
- already completed task -> idempotent no-op or explicit status;
- malformed deadline -> reject before storage;
- unsupported intent -> fall back to help/conversation, not a guessed mutation;
- stale confirmation token -> reject and rebuild action preview.

## Observability

Every mutation should eventually emit a compact audit event:

```text
actor / timestamp / intent / entity / before / after / source
```

This is useful both for debugging and for user-facing history such as "what changed in this project today?".
