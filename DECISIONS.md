# DevWork design decisions

These are intentionally short architecture decision records. The goal is to show why the system is shaped this way, not just what files exist.

## ADR-001 — deterministic command layer first

**Decision:** supported DevWork actions are represented by explicit application intents instead of allowing free-form AI output to call arbitrary storage functions.

**Why:** project-management mutations are easy to express in natural language but dangerous to guess. "Move it to Friday" can be ambiguous if several tasks were discussed.

**Trade-off:** the router supports fewer phrasings initially, but behaviour is testable and predictable.

## ADR-002 — confirmation before mutations

**Decision:** read-only requests can execute immediately; data-changing requests produce an action proposal that must be confirmed.

**Why:** chat UIs encourage short, context-dependent messages and accidental actions are difficult to notice after the fact.

**Trade-off:** one extra interaction for writes.

## ADR-003 — stages are first-class entities

**Decision:** implementation stages are stored explicitly rather than inferred from task tags.

**Why:** a project should preserve its implementation plan and explain how each task advances it.

**Trade-off:** slightly richer data model and more consistency rules.

## ADR-004 — daily planning is deterministic

**Decision:** the first planner ranks actionable tasks using transparent factors such as deadline distance, priority and blocked/completed state.

**Why:** users should be able to understand why a task was suggested for today.

**Trade-off:** the first version is less flexible than an ML/LLM scheduler, but easier to test and improve.

## ADR-005 — UI adapters do not own business logic

**Decision:** Telegram is an adapter; task transitions, scheduling and confirmation live in application/domain code.

**Why:** the same core can later serve CLI, HTTP and tests without copying rules.

## ADR-006 — AI is optional, not a runtime dependency

**Decision:** DevWork remains functional without a paid external AI API.

**Why:** deterministic project management should not stop working because an AI provider is unavailable, expensive or rate-limited.

**Trade-off:** conversational quality is an enhancement rather than the foundation of the product.
