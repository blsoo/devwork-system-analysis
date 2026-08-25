# DevWork — test cases

These are black-box/system-level cases derived from the public requirements and use cases. Unit tests for the Python prototype live separately.

| ID | Scenario | Preconditions | Steps | Expected result |
|---|---|---|---|---|
| TC-01 | Read project tasks | Project exists | Request project tasks | Task list is returned; no mutation proposal is created |
| TC-02 | Filter tasks by status | Project contains `todo` and `done` tasks | Request tasks with `status=todo` | Only `todo` tasks are returned |
| TC-03 | Create completion proposal | Task exists and is not done | Request `complete_task` | Proposal + preview are returned; task remains unchanged |
| TC-04 | Confirm completion proposal | Valid pending proposal exists | Confirm proposal once | Target task becomes done; success is returned |
| TC-05 | Repeat confirmation | Proposal was already applied | Confirm same proposal again | No second business mutation; stable already-applied result |
| TC-06 | Expired/stale proposal | Proposal is not valid anymore | Confirm proposal | Request is rejected; task state remains unchanged |
| TC-07 | Unknown task | Task id does not exist | Request completion proposal | Not-found error; no proposal is created |
| TC-08 | Unsupported free text | No supported intent matches | Send ambiguous text | `unknown`/unsupported outcome; no mutation |
| TC-09 | Planner excludes done | Project contains done + todo tasks | Request daily plan | Done task is absent from plan |
| TC-10 | Planner excludes blocked | Project contains blocked + todo tasks | Request daily plan | Blocked task is absent from plan |
| TC-11 | Planner explains ranking | At least one actionable task exists | Request daily plan | Every returned item contains one or more ranking reasons |
| TC-12 | Empty actionable plan | All tasks are blocked/done | Request daily plan | Empty plan is returned; system does not invent work |

## Detailed case — TC-04

**Title:** Confirm a pending task-completion proposal

**Preconditions**

- Task `17` exists.
- Task `17` status is `doing` or `todo`.
- A valid pending proposal exists for `complete_task(task_id=17)`.

**Steps**

1. Send confirmation for the proposal identifier.
2. Read task `17`.
3. Read the proposal state/audit outcome.

**Expected result**

- confirmation succeeds;
- task `17` status becomes `done`;
- proposal is no longer pending;
- an audit outcome exists;
- no unrelated task is modified.

## Detailed case — TC-05

**Title:** Repeated confirmation is idempotent

**Preconditions**

- TC-04 completed successfully.

**Steps**

1. Repeat confirmation for the same proposal identifier.
2. Read task `17`.
3. Compare mutation/audit effects with the first confirmation.

**Expected result**

- task remains `done`;
- the completion mutation is not applied twice;
- response is stable and indicates the already-applied state or equivalent;
- no duplicate business-side effect appears.
