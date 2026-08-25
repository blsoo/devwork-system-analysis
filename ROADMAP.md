# DevWork roadmap

The roadmap keeps future work tied to explicit engineering questions instead of a generic feature wishlist.

## Now

### Persistent storage — [Issue #1](https://github.com/blsoo/devwork-system-analysis/issues/1)

Move from in-memory storage to a persistent repository + migrations while preserving the domain/application boundary.

Key questions:
- transaction boundary for confirmation + task mutation + audit;
- stale-state handling;
- DB constraint vs application validation ownership.

### Recurring tasks — [Issue #2](https://github.com/blsoo/devwork-system-analysis/issues/2)

Implement the analysed change request from `CHANGE_REQUEST_EXAMPLE.md`.

Key questions:
- rule identity vs generated task identity;
- timezone;
- history preservation;
- scheduler idempotency.

## Next

- thin HTTP adapter matching `openapi.yaml`;
- fuller audit persistence and read API;
- project/stage progress projections;
- authorization boundary for multi-user projects;
- integration tests around concurrent confirmation.

## Later

- Telegram adapter using the same application services;
- calendar constraints and schedule blocks;
- optional read-only conversational assistant context;
- metrics/observability around command outcomes;
- richer workflow/state modelling where requirements justify it.

## Definition of portfolio-ready change

A meaningful change is not complete until the affected artifacts are reviewed:

`requirement -> business rule/use case -> data model -> API -> implementation -> tests -> traceability`

Not every change touches every layer, but the impact must be considered explicitly.
