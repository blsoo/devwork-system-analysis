# DevWork business rules

This document makes important domain rules explicit instead of leaving them implicit in handlers or UI code.

## Project and stage rules

**BR-01 — Project identity**  
Every project has a stable unique identifier. A project name is display data and is not used as identity.

**BR-02 — Stage ownership**  
A stage belongs to exactly one project.

**BR-03 — Stage order**  
Stages inside one project have an explicit order. Reordering changes execution order but does not change task identity.

**BR-04 — Derived progress**  
Stage/project progress should be derived from authoritative task/stage state where practical instead of being independently editable in multiple places.

## Task rules

**BR-05 — Task ownership**  
A task belongs to exactly one project.

**BR-06 — Optional stage relation**  
A task may belong to one stage or remain directly attached to the project when it has not yet been planned into a stage.

**BR-07 — Allowed task states**  
A task uses a controlled state set: `todo`, `doing`, `blocked`, `done`.

**BR-08 — Completed work is not actionable**  
Tasks in `done` are excluded from the daily actionable plan.

**BR-09 — Blocked work is not actionable**  
Tasks in `blocked` are not selected as executable daily work until unblocked.

## Mutation safety rules

**BR-10 — Intent is not authorization**  
Recognizing that a user wants to change state does not itself authorize that state change.

**BR-11 — Preview before mutation**  
A supported mutation first creates an action proposal describing the exact intended change.

**BR-12 — Explicit confirmation**  
The application may apply a proposal only after explicit confirmation while the proposal is still valid.

**BR-13 — Stored proposal is authoritative**  
Confirmation applies the payload stored in the proposal. A confirmation request cannot silently replace the target entity or operation parameters.

**BR-14 — Proposal expiry**  
Expired proposals cannot mutate state.

**BR-15 — Stale-state validation**  
Before applying a proposal, the service re-validates the current domain state. A proposal that is no longer valid fails without mutation.

**BR-16 — Idempotent confirmation**  
Repeating confirmation for an already successfully confirmed proposal must not repeat the business side effect.

**BR-17 — Audit after mutation**  
A successful mutation produces an audit event describing what changed.

## Conversational rules

**BR-18 — Unknown text is not guessed into a write**  
Unsupported or ambiguous free text must not be converted into a destructive/data-changing intent by guesswork.

**BR-19 — Read-only queries may execute directly**  
Known read-only intents can execute without the mutation-confirmation flow.

**BR-20 — Adapter independence**  
Telegram, CLI and future web/API clients use the same application rules. A UI adapter must not implement a separate private version of the business logic.

## Daily planning rules

**BR-21 — Deterministic first version**  
The initial planner ranks work using explicit inputs such as priority, deadline proximity, overdue state and already-started work.

**BR-22 — Explainable ranking**  
Every ranked task should expose reasons for its priority so the user can understand why it appears in the plan.

**BR-23 — No hidden LLM authority**  
An optional conversational/AI layer may suggest or explain, but application state changes still pass through supported deterministic commands and confirmation rules.

## Why this file exists

A system analyst should be able to point to a rule and then trace it to:

- a use case;
- a state transition;
- an API behaviour;
- a database constraint where applicable;
- one or more tests.

That is more maintainable than relying on someone to infer business rules from implementation code.
