# DevWork domain glossary

A small glossary keeps the same words meaning the same things across requirements, API, database and UI discussions.

| Term | Meaning | Not the same as |
|---|---|---|
| **Project** | Work context containing goal, specification, stages and tasks | A flat todo list |
| **Stage** | Ordered implementation step inside a project | Task status |
| **Task** | Actionable work item belonging to one project | Stage or project goal |
| **Actionable task** | Task currently eligible for planning/execution | Any task in storage |
| **Action proposal** | Stored preview of one intended state-changing action | The mutation itself |
| **Confirmation** | Explicit authorization to apply the exact stored proposal | Re-sending arbitrary mutation parameters |
| **Daily plan** | Ranked projection of actionable tasks | Independent copy of task state |
| **Audit event** | Record of a mutation outcome | Application log line |
| **Intent** | Known application-level meaning recognized from user input | Permission to execute |
| **Adapter** | Telegram/CLI/HTTP boundary translating external input to application calls | Owner of business rules |
| **Stale proposal** | Proposal whose assumptions no longer match current domain state | Malformed request |
| **Idempotency** | Repeating the same logical operation does not repeat its business effect | Ignoring all duplicates blindly |

## Naming rules

- IDs are stable identity; names/titles are display data.
- `project_id` means a relation to a project, not the project title.
- `status` values come from controlled sets.
- Terms used in API fields should map cleanly to domain concepts.
- UI wording may be friendlier, but must not silently change business meaning.

## Why this matters

A lot of integration bugs start as vocabulary bugs: two people use the same word for different states, or different words for the same entity. A glossary makes requirements, diagrams, SQL and API discussions easier to review together.
