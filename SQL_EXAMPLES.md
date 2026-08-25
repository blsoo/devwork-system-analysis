# DevWork SQL examples

These examples use the public DevWork data model and show the kind of SQL a system analyst may need to read, discuss or verify.

Assume simplified tables:

```text
projects(id, name, status)
stages(id, project_id, title, position, status)
tasks(id, project_id, stage_id, title, status, priority, deadline)
action_proposals(id, project_id, action_type, status, expires_at)
audit_events(id, event_type, entity_id, created_at)
```

## 1. Active tasks of one project

```sql
SELECT id, title, status, priority, deadline
FROM tasks
WHERE project_id = 5
  AND status <> 'done'
ORDER BY priority DESC, deadline ASC NULLS LAST;
```

## 2. Tasks with no deadline

```sql
SELECT id, title
FROM tasks
WHERE project_id = 5
  AND deadline IS NULL;
```

## 3. Latest completed task

```sql
SELECT id, title
FROM tasks
WHERE project_id = 5
  AND status = 'done'
ORDER BY id DESC
LIMIT 1;
```

## 4. Task with project name

```sql
SELECT
    t.id,
    t.title,
    t.status,
    p.name AS project_name
FROM tasks t
JOIN projects p ON p.id = t.project_id
WHERE t.id = 17;
```

The foreign key stores the relationship; `JOIN` uses it to read related data together.

## 5. Keep projects even when they have no tasks

```sql
SELECT
    p.id,
    p.name,
    t.id AS task_id,
    t.title
FROM projects p
LEFT JOIN tasks t ON t.project_id = p.id
ORDER BY p.id, t.id;
```

## 6. Find projects with no tasks

```sql
SELECT p.id, p.name
FROM projects p
LEFT JOIN tasks t ON t.project_id = p.id
WHERE t.id IS NULL;
```

## 7. Count completed tasks in a project

```sql
SELECT COUNT(*) AS completed_tasks
FROM tasks
WHERE project_id = 5
  AND status = 'done';
```

## 8. Count tasks by status

```sql
SELECT status, COUNT(*) AS task_count
FROM tasks
WHERE project_id = 5
GROUP BY status
ORDER BY status;
```

## 9. Stage progress view

```sql
SELECT
    s.id,
    s.title,
    COUNT(t.id) AS total_tasks,
    COUNT(t.id) FILTER (WHERE t.status = 'done') AS done_tasks
FROM stages s
LEFT JOIN tasks t ON t.stage_id = s.id
WHERE s.project_id = 5
GROUP BY s.id, s.title
ORDER BY s.position;
```

This is an example of deriving progress-related data from task state rather than storing several conflicting manual counters.

## 10. Pending action proposals

```sql
SELECT id, action_type, expires_at
FROM action_proposals
WHERE project_id = 5
  AND status = 'pending'
ORDER BY expires_at;
```

## 11. Expired proposals still marked pending

```sql
SELECT id, project_id, action_type, expires_at
FROM action_proposals
WHERE status = 'pending'
  AND expires_at < CURRENT_TIMESTAMP;
```

This query can support cleanup/monitoring, but expiry must still be validated by the command path itself.

## 12. Recent audit history

```sql
SELECT event_type, entity_id, created_at
FROM audit_events
ORDER BY created_at DESC
LIMIT 20;
```

## What an interviewer can ask

- Why is `project_id` a foreign key?
- Why use `LEFT JOIN` instead of `JOIN` when looking for projects without tasks?
- Why is `IS NULL` used instead of `= NULL`?
- What does `COUNT(*)` count?
- Why can a derived progress query be safer than an independently editable progress field?
- What index might help `WHERE project_id = ? AND status = ?`?
- Why should an expired proposal check exist in application logic even if a SQL query can find expired rows?
