from datetime import date, timedelta
import unittest

from devwork_core import (
    ActionProposal,
    CommandService,
    DailyPlanner,
    InMemoryTaskRepository,
    IntentKind,
    IntentRouter,
    ParsedIntent,
    Task,
    TaskStatus,
)


class IntentRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = IntentRouter()

    def test_read_only_task_list_is_not_marked_as_mutation(self) -> None:
        intent = self.router.parse("покажи задачи")
        self.assertEqual(IntentKind.SHOW_TASKS, intent.kind)
        self.assertFalse(intent.mutates_state)

    def test_complete_task_is_parsed_as_confirmation_gated_mutation(self) -> None:
        intent = self.router.parse("закрой задачу 42")
        self.assertEqual(IntentKind.COMPLETE_TASK, intent.kind)
        self.assertEqual(42, intent.task_id)
        self.assertTrue(intent.mutates_state)

    def test_unsupported_phrase_does_not_guess_a_mutation(self) -> None:
        intent = self.router.parse("сделай с этой задачей что-нибудь")
        self.assertEqual(IntentKind.UNKNOWN, intent.kind)
        self.assertFalse(intent.mutates_state)


class ConfirmationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = InMemoryTaskRepository([Task(7, 1, "Write tests")])
        self.commands = CommandService(self.repo)

    def test_proposal_does_not_modify_storage(self) -> None:
        intent = ParsedIntent(IntentKind.COMPLETE_TASK, task_id=7, mutates_state=True)
        proposal = self.commands.propose(intent)
        self.assertIn("Write tests", proposal.summary)
        self.assertEqual(TaskStatus.TODO, self.repo.get(7).status)

    def test_confirmation_applies_exact_proposal(self) -> None:
        intent = ParsedIntent(IntentKind.COMPLETE_TASK, task_id=7, mutates_state=True)
        proposal = self.commands.propose(intent)
        updated = self.commands.confirm(proposal)
        self.assertEqual(TaskStatus.DONE, updated.status)
        self.assertEqual(TaskStatus.DONE, self.repo.get(7).status)

    def test_repeated_confirmation_is_idempotent(self) -> None:
        proposal = ActionProposal(
            ParsedIntent(IntentKind.COMPLETE_TASK, task_id=7, mutates_state=True),
            "complete #7",
        )
        first = self.commands.confirm(proposal)
        second = self.commands.confirm(proposal)
        self.assertEqual(first, second)


class PlannerTests(unittest.TestCase):
    def test_overdue_high_priority_task_ranks_before_later_work(self) -> None:
        today = date(2026, 8, 25)
        tasks = [
            Task(1, 1, "Overdue", priority=1, deadline=today - timedelta(days=1)),
            Task(2, 1, "Later", priority=2, deadline=today + timedelta(days=10)),
        ]
        ranked = DailyPlanner().rank(tasks, today)
        self.assertEqual(1, ranked[0].task.id)
        self.assertIn("overdue by 1d", ranked[0].reasons)

    def test_done_and_blocked_tasks_are_not_scheduled(self) -> None:
        today = date(2026, 8, 25)
        tasks = [
            Task(1, 1, "Done", status=TaskStatus.DONE),
            Task(2, 1, "Blocked", status=TaskStatus.BLOCKED),
            Task(3, 1, "Actionable", status=TaskStatus.TODO),
        ]
        ranked = DailyPlanner().rank(tasks, today)
        self.assertEqual([3], [item.task.id for item in ranked])


if __name__ == "__main__":
    unittest.main()
