-- Portfolio schema draft for DevWork.
-- PostgreSQL-oriented and intentionally independent from any production data.

create table projects (
    id bigint generated always as identity primary key,
    name text not null,
    goal text not null,
    specification text not null default '',
    status text not null default 'active'
        check (status in ('planned', 'active', 'paused', 'done', 'archived')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table stages (
    id bigint generated always as identity primary key,
    project_id bigint not null references projects(id) on delete cascade,
    title text not null,
    description text not null default '',
    position integer not null check (position > 0),
    status text not null default 'planned'
        check (status in ('planned', 'active', 'blocked', 'done')),
    unique (project_id, position)
);

create table tasks (
    id bigint generated always as identity primary key,
    project_id bigint not null references projects(id) on delete cascade,
    stage_id bigint references stages(id) on delete set null,
    title text not null,
    description text not null default '',
    status text not null default 'todo'
        check (status in ('todo', 'doing', 'blocked', 'done')),
    priority smallint not null default 2 check (priority between 1 and 5),
    deadline timestamptz,
    estimate_minutes integer check (estimate_minutes is null or estimate_minutes > 0),
    created_at timestamptz not null default now(),
    completed_at timestamptz,
    constraint completed_state_consistency check (
        (status = 'done' and completed_at is not null)
        or (status <> 'done' and completed_at is null)
    )
);

create index tasks_project_status_idx on tasks(project_id, status);
create index tasks_deadline_idx on tasks(deadline) where status in ('todo', 'doing');
create index tasks_stage_idx on tasks(stage_id) where stage_id is not null;

create table action_proposals (
    id uuid primary key,
    actor_id bigint not null,
    intent text not null,
    payload jsonb not null,
    preview text not null,
    state text not null default 'pending'
        check (state in ('pending', 'confirmed', 'expired', 'cancelled')),
    created_at timestamptz not null default now(),
    expires_at timestamptz not null,
    confirmed_at timestamptz,
    check (expires_at > created_at)
);

create table audit_events (
    id bigint generated always as identity primary key,
    actor_id bigint not null,
    source text not null,
    intent text not null,
    entity_type text not null,
    entity_id bigint,
    before_state jsonb,
    after_state jsonb,
    created_at timestamptz not null default now()
);

create index audit_events_entity_idx
    on audit_events(entity_type, entity_id, created_at desc);
