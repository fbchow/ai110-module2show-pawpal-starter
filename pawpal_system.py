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

from dataclasses import dataclass, field
from enum import IntEnum


class Priority(IntEnum):
    """Task priority. Int-ranked so higher priority sorts higher."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    """A single care activity for a pet."""

    description: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    time: str | None = None          # scheduled slot, e.g. "08:00"; set by the planner
    done: bool = False
    pet: "Pet | None" = None         # owning pet; set by Pet.add_task

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.done = True

    def mark_undone(self) -> None:
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

    def tasks_by_priority(self, owner: Owner) -> list[Task]:
        """All tasks sorted by priority (high first), then shorter tasks first."""
        return sorted(
            owner.all_tasks(),
            key=lambda t: (-t.priority, t.duration_minutes),
        )

    def todays_tasks(self, owner: Owner) -> list[Task]:
        """Tasks that belong on today's plan: those given a scheduled time."""
        return [t for t in owner.all_tasks() if t.time is not None]

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
