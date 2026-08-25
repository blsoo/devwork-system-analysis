# DevWork API contract draft

This is a public-safe contract sketch for the future HTTP adapter. Business rules remain in the application layer.

## Read operations

### `GET /projects/{project_id}`

Returns goal, specification summary, active stage and aggregate progress.

### `GET /projects/{project_id}/tasks?status=todo`

Returns project tasks with optional stage/status filters.

### `GET /projects/{project_id}/today`

Returns the deterministic daily plan with ranking explanations.

Example:

```json
{
  "date": "2026-08-25",
  "items": [
    {
      "task_id": 17,
      "title": "Add confirmation flow",
      "score": 90,
      "reasons": ["priority P1", "due today"]
    }
  ]
}
```

## Mutation flow

Mutations are intentionally two-step.

### `POST /actions/proposals`

Request:

```json
{
  "intent": "complete_task",
  "payload": {"task_id": 17}
}
```

Response:

```json
{
  "proposal_id": "b4f3...",
  "preview": "Mark task #17 'Add confirmation flow' as done",
  "expires_at": "2026-08-25T17:20:00+03:00"
}
```

No task state is changed at this point.

### `POST /actions/proposals/{proposal_id}/confirm`

Applies the exact stored proposal if it is still pending and valid.

Expected properties:

- repeated confirmation is idempotent;
- expired proposal is rejected;
- changing the task id requires a new proposal;
- the mutation emits an audit event.

## Error model

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task 17 does not exist"
  }
}
```

Suggested status mapping:

- `400` invalid request;
- `404` entity not found;
- `409` invalid state transition / stale proposal;
- `422` understood request that violates a domain rule.

## Why two-step writes

The API mirrors the chat safety model. Understanding a sentence such as "finish task 17" and actually changing stored state are different operations. Keeping them separate makes Telegram, CLI and HTTP clients follow the same rule instead of implementing their own safety behaviour.
