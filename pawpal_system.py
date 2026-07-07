"""PawPal+ core domain model.

Derived from the UML draft in diagrams/uml.mmd.

Model overview:
    Task    - a single care activity (description, time, done).
    Pet     - pet details plus the list of tasks that belong to it.
    Owner   - manages multiple pets and aggregates all their tasks.
    Scheduler - stateless "brain" that retrieves and organizes tasks across
                an owner's pets and builds a daily plan.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, IntEnum


class Priority(IntEnum):
    """Task priority. Int-ranked so higher priority sorts higher."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(str, Enum):
    """How often a task recurs. ONCE tasks do not repeat."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


# How far ahead the next occurrence of a recurring task is scheduled.
_RECUR_DELTAS = {
    Frequency.DAILY: timedelta(days=1),
    Frequency.WEEKLY: timedelta(weeks=1),
}


@dataclass
class Task:
    """A single care activity for a pet."""

    description: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    time: str | None = None          # scheduled slot, e.g. "08:00"; set by the planner
    done: bool = False
    pet: "Pet | None" = None         # owning pet; set by Pet.add_task
    frequency: Frequency = Frequency.ONCE
    due_date: date | None = None     # when this occurrence is due

    def mark_complete(self) -> None:
        """Mark this task done; for daily/weekly tasks, spawn the next occurrence."""
        self.done = True
        delta = _RECUR_DELTAS.get(self.frequency)
        if delta is None or self.pet is None:
            return
        # daily -> today + 1 day, weekly -> today + 7 days (calendar-safe).
        next_task = Task(
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time=self.time,
            frequency=self.frequency,
            due_date=date.today() + delta,
        )
        self.pet.add_task(next_task)

    def mark_incomplete(self) -> None:
        """Reopen a completed task."""
        self.done = False

    def cancel(self) -> None:
        """Detach this task from its pet's task list."""
        if self.pet is not None:
            self.pet.remove_task(self)


@dataclass
class Pet:
    """A pet, its details, and the tasks that belong to it."""

    name: str
    species: str  # "dog" | "cat" | "other"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if present."""
        if task in self.tasks:
            self.tasks.remove(task)
            task.pet = None

    def pending_tasks(self) -> list[Task]:
        """Return this pet's incomplete tasks."""
        return [t for t in self.tasks if not t.done]

    def eat(self) -> None:
        """Record a feeding for this pet (behavioral hook, no state yet)."""
        ...

    def sleep(self) -> None:
        """Record a rest period for this pet (behavioral hook, no state yet)."""
        ...


@dataclass
class Owner:
    """The pet owner. Manages multiple pets and their combined tasks."""

    name: str
    experience: str = ""  # e.g. "beginner", "experienced"
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flatten every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Stateless brain that retrieves and organizes tasks across an owner's pets.

    It talks to the Owner (via all_tasks) rather than reaching into each Pet's
    storage, so it stays decoupled from how pets hold their tasks.
    """

    def all_tasks(self, owner: Owner) -> list[Task]:
        """Every task the owner has, across all pets."""
        return owner.all_tasks()

    def pending_tasks(self, owner: Owner) -> list[Task]:
        """Incomplete tasks across all of the owner's pets."""
        return [t for t in owner.all_tasks() if not t.done]

    def filter_tasks(
        self,
        owner: Owner,
        done: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Filter the owner's tasks by completion status and/or pet name.

        Both filters are optional and combine with AND. When both are None,
        returns all tasks (equivalent to all_tasks). Pet-name matching is
        case-insensitive.
        """
        tasks = owner.all_tasks()
        if done is not None:
            tasks = [t for t in tasks if t.done == done]
        if pet_name is not None:
            tasks = [
                t
                for t in tasks
                if t.pet is not None and t.pet.name.lower() == pet_name.lower()
            ]
        return tasks

    def tasks_by_priority(self, owner: Owner) -> list[Task]:
        """All tasks sorted by priority (high first), then shorter tasks first."""
        return sorted(
            owner.all_tasks(),
            key=lambda t: (-t.priority, t.duration_minutes),
        )

    def sort_by_time(self, owner: Owner) -> list[Task]:
        """All tasks sorted by scheduled time (ascending). Untimed tasks last.

        "HH:MM" strings are zero-padded, so lexicographic order matches clock
        order and no parsing is needed. The (time is None, ...) key pushes
        untimed tasks to the end.
        """
        return sorted(
            owner.all_tasks(),
            key=lambda t: (t.time is None, t.time or ""),
        )

    def todays_tasks(self, owner: Owner) -> list[Task]:
        """Tasks that belong on today's plan: those given a scheduled time."""
        return [t for t in owner.all_tasks() if t.time is not None]

    def find_conflicts(self, owner: Owner) -> list[str]:
        """Detect tasks scheduled for the same clock slot.

        Lightweight, non-crashing check: groups all *timed* tasks by their
        "HH:MM" slot and, for any slot holding 2+ tasks, returns a readable
        warning string naming the time and each colliding task with its pet.
        Untimed tasks (time is None) are skipped — they occupy no slot. Returns
        an empty list when there are no conflicts, so the caller decides how to
        surface (or ignore) them.
        """
        by_slot: dict[str, list[Task]] = defaultdict(list)
        for task in owner.all_tasks():
            if task.time is not None:
                by_slot[task.time].append(task)

        warnings: list[str] = []
        for slot in sorted(by_slot):
            tasks = by_slot[slot]
            if len(tasks) < 2:
                continue
            joined = ", ".join(
                f"'{t.description}' ({t.pet.name if t.pet else '—'})" for t in tasks
            )
            warnings.append(f"Conflict at {slot}: {joined}")
        return warnings

    def has_conflicts(self, owner: Owner) -> bool:
        """True if any two tasks share a scheduled time slot."""
        return bool(self.find_conflicts(owner))

    def build_plan(self, owner: Owner, available_minutes: int) -> list[Task]:
        """Select and order pending tasks that fit within a time budget.

        Greedy by priority: highest-priority tasks first, including a task only
        if its duration still fits the remaining budget. Returns a fresh ordered
        list and does NOT mutate any pet's task list.
        """
        remaining = available_minutes
        plan: list[Task] = []
        for task in self.tasks_by_priority(owner):
            if task.done:
                continue
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
        return plan


def format_plan(plan: list[Task]) -> str:
    """Render a plan as a readable, time-ordered terminal agenda.

    Tasks are sorted by scheduled time (ascending), ties broken by priority
    (HIGH first); untimed tasks are listed last. Each row shows its pet.
    Ends with a total-time summary.
    """
    if not plan:
        return "No tasks scheduled."

    ordered = sorted(plan, key=lambda t: (t.time is None, t.time or "", -t.priority))

    lines = ["Daily plan"]
    for t in ordered:
        slot = t.time or "--:--"
        pet_name = t.pet.name if t.pet else "—"
        lines.append(
            f"  {slot}  {t.description:<18}  {pet_name:<10}  {t.duration_minutes:>3} min  [{t.priority.name}]"
        )

    total = sum(t.duration_minutes for t in plan)
    lines.append("")
    lines.append(f"Total: {total} min across {len(plan)} tasks")
    return "\n".join(lines)
