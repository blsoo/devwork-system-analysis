# DevWork five-minute demo

The point of the demo is not to show every feature. It is to demonstrate the architecture through one safe read and one safe mutation.

## 1. Start with the problem

"Projects usually lose context between idea, specification, implementation plan and daily tasks. DevWork keeps those layers connected and lets a chat interface operate on top of them."

## 2. Show the model

Open `DATA_MODEL.md` and explain:

```text
Project -> Stage -> Task
```

The project stores *why* it exists, the stage stores *where implementation is*, and the task stores *what can be done next*.

## 3. Show a read-only intent

Input:

```text
покажи задачи
```

Router result:

```text
SHOW_TASKS / mutates_state=false
```

Nothing needs confirmation.

## 4. Show a mutation

Input:

```text
закрой задачу 7
```

Router result:

```text
COMPLETE_TASK(task_id=7) / mutates_state=true
```

The command service first creates a preview:

```text
Mark task #7 "Write tests" as done
```

At this point storage is unchanged.

Only explicit confirmation applies the mutation.

## 5. Show the tests

From `prototype`:

```bash
python -m unittest -v test_devwork_core.py
```

Call out these behaviours:

- unsupported text does not guess a mutation;
- proposal creation does not change storage;
- confirmation changes exactly the proposed task;
- repeated confirmation is idempotent;
- completed and blocked tasks are excluded from the daily plan.

## 6. Show the planner

Explain that the first planner is intentionally transparent rather than "AI-powered".

It ranks actionable work from factors the user can inspect:

- priority;
- overdue status;
- deadline distance;
- already-in-progress state.

A future conversational assistant may explain the result, but the ranking has a deterministic baseline.

## 7. Close with the trade-off

"I could let an LLM directly call database functions, but I do not want natural-language ambiguity to become an uncontrolled write path. DevWork uses AI as an assistant around deterministic application actions, not as the authority over state."

That is the core engineering idea of the project.
