# DevWork API examples

Concrete request/response examples for the public API contract. Values are synthetic.

## Get project

```http
GET /projects/5
Accept: application/json
```

```json
{
  "id": 5,
  "name": "DevWork",
  "goal": "Keep project context and execution connected",
  "specification_summary": "Projects, stages, tasks and daily planning",
  "status": "active",
  "active_stage_id": 12,
  "progress": 46
}
```

## List project tasks

```http
GET /projects/5/tasks?status=todo
Accept: application/json
```

```json
[
  {
    "id": 17,
    "project_id": 5,
    "stage_id": 12,
    "title": "Add persistence adapter",
    "status": "todo",
    "priority": 1,
    "deadline": "2026-08-29T18:00:00Z"
  }
]
```

## Create a mutation proposal

The request describes intent. It does **not** mutate the task yet.

```http
POST /actions/proposals
Content-Type: application/json
```

```json
{
  "intent": "complete_task",
  "payload": {
    "task_id": 17
  }
}
```

```http
HTTP/1.1 201 Created
```

```json
{
  "proposal_id": "p-demo-42",
  "preview": "Mark task #17 'Add persistence adapter' as done",
  "status": "pending",
  "expires_at": "2026-08-25T23:10:00Z"
}
```

## Confirm a proposal

```http
POST /actions/proposals/p-demo-42/confirm
```

```json
{
  "proposal_id": "p-demo-42",
  "status": "applied",
  "applied": true,
  "target_task_id": 17
}
```

## Repeat confirmation

A network retry must not repeat the business effect.

```http
POST /actions/proposals/p-demo-42/confirm
```

```json
{
  "proposal_id": "p-demo-42",
  "status": "already_applied",
  "applied": false,
  "target_task_id": 17
}
```

## Stale-state conflict

If the task changed after proposal creation and the stored transition is no longer valid:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "error": {
    "code": "STALE_PROPOSAL",
    "message": "The target state changed; create a new proposal"
  }
}
```

## Invalid input vs invalid business state

The portfolio keeps these cases separate:

- `400 Bad Request` — malformed request shape/syntax;
- `404 Not Found` — referenced entity does not exist;
- `409 Conflict` — request conflicts with current state;
- `422 Unprocessable Content` — understood request violates a domain rule.

The exact error taxonomy may evolve, but the important analyst decision is to make failure semantics explicit and testable.
