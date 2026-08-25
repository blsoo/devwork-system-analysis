"""Small executable prototype for the DevWork application core.

The module intentionally has no Telegram, database or LLM dependency. It keeps
business rules testable before adapters and infrastructure are introduced.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from enum import Enum
import re
from typing import Iterable


class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    BLOCKED = "blocked"
    DONE = "done"


class IntentKind(str, Enum):
    SHOW_TASKS = "show_tasks"
    SHOW_TODAY = "show_today"
    COMPLETE_TASK = "complete_task"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    goal: str
    specification: str = ""


@dataclass(frozen=True)
class Stage:
    id: int
    project_id: int
    title: str
    position: int
    status: str = "planned"


@dataclass(frozen=True)
class Task:
    id: int
    project_id: int
    title: str
    stage_id: int | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = 2  # 1=highest, 5=lowest
    deadline: date | None = None
    estimate_minutes: int | None = None

    @property
    def actionable(self) -> bool:
        return self.status in {TaskStatus.TODO, TaskStatus.DOING}


@dataclass(frozen=True)
class ParsedIntent:
    kind: IntentKind
    task_id: int | None = None
    mutates_state: bool = False


@dataclass(frozen=True)
class ActionProposal:
    intent: ParsedIntent
    summary: str


@dataclass(frozen=True)
class PlannedTask:
    task: Task
    score: int
    reasons: tuple[str, ...] = field(default_factory=tuple)


class IntentRouter:
    """Maps a deliberately small set of natural-language phrases to intents."""

    _complete_patterns = (
        re.compile(r"^(?:закрой|заверши|выполни)\s+(?:задачу\s+)?#?(\d+)$", re.I),
        re.compile(r"^(?:complete|finish)\s+(?:task\s+)?#?(\d+)$", re.I),
    )

    def parse(self, text: str) -> ParsedIntent:
        normalized = " ".join(text.strip().split())

        for pattern in self._complete_patterns:
            match = pattern.match(normalized)
            if match:
                return ParsedIntent(
                    kind=IntentKind.COMPLETE_TASK,
                    task_id=int(match.group(1)),
                    mutates_state=True,
                )

        lowered = normalized.lower()
        if lowered in {
            "покажи задачи",
            "мои задачи",
            "show tasks",
            "list tasks",
        }:
            return ParsedIntent(IntentKind.SHOW_TASKS)

        if lowered in {
            "что сегодня",
            "что делать сегодня",
            "план на сегодня",
            "today",
            "today plan",
        }:
            return ParsedIntent(IntentKind.SHOW_TODAY)

        return ParsedIntent(IntentKind.UNKNOWN)


class InMemoryTaskRepository:
    """Infrastructure placeholder with repository-like behaviour."""

    def __init__(self, tasks: Iterable[Task] = ()) -> None:
        self._tasks = {task.id: task for task in tasks}

    def get(self, task_id: int) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise KeyError(f"task {task_id} does not exist") from exc

    def list_for_project(self, project_id: int) -> list[Task]:
        return [task for task in self._tasks.values() if task.project_id == project_id]

    def save(self, task: Task) -> None:
        self._tasks[task.id] = task


class CommandService:
    """Builds mutation previews and applies only explicitly confirmed actions."""

    def __init__(self, tasks: InMemoryTaskRepository) -> None:
        self.tasks = tasks

    def propose(self, intent: ParsedIntent) -> ActionProposal:
        if not intent.mutates_state:
            raise ValueError("read-only intents do not need confirmation")

        if intent.kind is IntentKind.COMPLETE_TASK and intent.task_id is not None:
            task = self.tasks.get(intent.task_id)
            return ActionProposal(
                intent=intent,
                summary=f'Mark task #{task.id} "{task.title}" as done',
            )

        raise ValueError("unsupported mutation")

    def confirm(self, proposal: ActionProposal) -> Task:
        intent = proposal.intent
        if intent.kind is not IntentKind.COMPLETE_TASK or intent.task_id is None:
            raise ValueError("unsupported mutation")

        current = self.tasks.get(intent.task_id)
        if current.status is TaskStatus.DONE:
            return current  # idempotent confirmation

        updated = replace(current, status=TaskStatus.DONE)
        self.tasks.save(updated)
        return updated


class DailyPlanner:
    """Transparent first-pass scheduler, intentionally not ML-based."""

    def rank(self, tasks: Iterable[Task], today: date) -> list[PlannedTask]:
        planned: list[PlannedTask] = []

        for task in tasks:
            if not task.actionable:
                continue

            score = (6 - task.priority) * 10
            reasons: list[str] = [f"priority P{task.priority}"]

            if task.status is TaskStatus.DOING:
                score += 15
                reasons.append("already in progress")

            if task.deadline is not None:
                days = (task.deadline - today).days
                if days < 0:
                    score += 50
                    reasons.append(f"overdue by {-days}d")
                elif days == 0:
                    score += 40
                    reasons.append("due today")
                elif days <= 2:
                    score += 25
                    reasons.append(f"due in {days}d")
                elif days <= 7:
                    score += 10
                    reasons.append(f"due in {days}d")

            planned.append(PlannedTask(task, score, tuple(reasons)))

        return sorted(planned, key=lambda item: (-item.score, item.task.id))


def build_demo_state() -> tuple[Project, list[Stage], InMemoryTaskRepository]:
    project = Project(
        id=1,
        name="DevWork",
        goal="Keep project context, implementation stages and daily work connected",
    )
    stages = [
        Stage(1, 1, "Deterministic command layer", 1, "active"),
        Stage(2, 1, "Persistent storage", 2),
    ]
    tasks = InMemoryTaskRepository(
        [
            Task(1, 1, "Add confirmation flow", 1, priority=1),
            Task(2, 1, "Write router tests", 1, status=TaskStatus.DOING, priority=2),
            Task(3, 1, "Design database migrations", 2, priority=3),
        ]
    )
    return project, stages, tasks
