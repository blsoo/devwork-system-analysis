# DevWork — use cases

The use cases below describe behaviour at the system boundary. They intentionally avoid binding the business flow to Telegram, CLI or HTTP.

## UC-01 — View project tasks

**Primary actor:** User  
**Goal:** See tasks for a project without changing state.

**Preconditions**

- the project exists;
- the user has access to the project context.

**Main flow**

1. User requests project tasks.
2. Client adapter sends a read request.
3. Application validates the project identifier.
4. Application reads matching tasks.
5. System returns the task list.

**Alternative flows**

- Project does not exist -> return not-found error.
- Optional status filter is supplied -> return only matching tasks.

**Postcondition:** no task state is changed.

---

## UC-02 — Complete a task with confirmation

**Primary actor:** User  
**Goal:** Mark one task as done without allowing an accidental write.

**Preconditions**

- the task exists;
- the requested transition is allowed.

**Main flow**

1. User asks to complete a task.
2. System recognizes a supported mutating intent.
3. Application creates an action proposal.
4. System returns a preview describing the exact task and change.
5. User explicitly confirms the proposal.
6. Application verifies that the proposal is still pending and valid.
7. Application applies the stored mutation.
8. Application records the mutation outcome for audit.
9. System returns success.

**Alternative flows**

- Task does not exist -> reject proposal creation.
- Proposal expires/becomes stale -> reject confirmation.
- User does not confirm -> no mutation occurs.
- Requested transition violates a domain rule -> reject the action.

**Postcondition:** the task is done only after valid confirmation.

---

## UC-03 — Repeat confirmation safely

**Primary actor:** User / retrying client  
**Goal:** Prevent duplicate effects when the same confirmation is delivered again.

**Preconditions**

- a proposal was already confirmed successfully.

**Main flow**

1. Client repeats confirmation for the same proposal.
2. Application detects that the proposal is already applied.
3. Application does not execute the task mutation again.
4. System returns the stable already-applied result.

**Postcondition:** one logical user action produces one business mutation.

---

## UC-04 — Get today's plan

**Primary actor:** User  
**Goal:** Receive a prioritized list of actionable tasks with explanations.

**Preconditions**

- the project contains tasks.

**Main flow**

1. User requests today's plan.
2. Application loads candidate tasks.
3. Completed and blocked tasks are excluded.
4. Planner scores remaining tasks using transparent inputs.
5. Tasks are sorted by deterministic score/tie-break rules.
6. System returns ranked tasks with reasons.

**Alternative flow**

- No actionable tasks exist -> return an empty plan rather than inventing work.

**Postcondition:** project/task state is unchanged.

---

## UC-05 — Handle unsupported or ambiguous text

**Primary actor:** User  
**Goal:** Avoid accidental mutations from misunderstood natural language.

**Main flow**

1. User sends free text that does not map to a supported intent.
2. Intent router returns an unsupported/unknown classification.
3. System may ask the user to rephrase or choose a known action.
4. No mutation proposal is created automatically.
5. No storage change occurs.

**Postcondition:** ambiguous input is fail-safe.
