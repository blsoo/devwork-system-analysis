# DevWork — requirements traceability

This matrix links analyst artifacts to implementation/test evidence so that requirements do not live as isolated prose.

| Requirement | Use case | Interface / contract | Verification evidence |
|---|---|---|---|
| FR-01 Project structure | UC-01, UC-04 | `GET /projects/{project_id}` | `DATA_MODEL.md`, `schema.sql` |
| FR-02 Read project tasks | UC-01 | `GET /projects/{project_id}/tasks` | TC-01, TC-02 |
| FR-03 Read vs mutation split | UC-01, UC-02, UC-05 | intent router / application boundary | prototype intent-router tests |
| FR-04 Mutation proposal | UC-02 | `POST /actions/proposals` | TC-03; proposal-no-side-effect unit test |
| FR-05 Explicit confirmation | UC-02 | `POST /actions/proposals/{id}/confirm` | TC-04; confirmation unit test |
| FR-06 Idempotent confirmation | UC-03 | confirmation endpoint | TC-05; repeated-confirmation unit test |
| FR-07 Explainable daily plan | UC-04 | `GET /projects/{project_id}/today` | TC-09..TC-12; planner tests |
| FR-08 Audit mutation outcome | UC-02, UC-03 | application command service / audit storage | `schema.sql`, `DECISIONS.md` |
| FR-09 Fail safely on ambiguous input | UC-05 | intent router | TC-08; unsupported-text unit test |
| NFR-01 Safety | UC-02, UC-03, UC-05 | shared application service | confirmation + idempotency tests |
| NFR-02 Determinism | UC-04 | daily planner | deterministic planner tests |
| NFR-03 Explainability | UC-02, UC-04 | preview + planner reasons | TC-03, TC-11 |
| NFR-04 Separation of concerns | all | adapter/application split | `ARCHITECTURE.md` |
| NFR-05 Auditability | UC-02, UC-03 | audit events | schema + mutation workflow |
| NFR-06 Portability | all | dependency-free core | public Python prototype |

## Why keep a matrix

A requirement is useful only if a reviewer can answer three questions:

1. **Where is the behaviour exposed?**
2. **Where is it implemented or modelled?**
3. **How do we verify it?**

The matrix also makes change impact visible. For example, changing the confirmation rule should trigger review of FR-05/FR-06, UC-02/UC-03, the confirmation endpoint and the corresponding tests.
