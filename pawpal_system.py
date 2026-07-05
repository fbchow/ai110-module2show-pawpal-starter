"""PawPal+ core domain model.

Class skeleton derived from the UML draft in diagrams/uml.mmd.
Method bodies are intentionally left as stubs (no logic yet) — implement the
scheduling behavior in later steps, then connect it to app.py.
"""

from dataclasses import dataclass, field


@dataclass
class Pet:
    """A pet that care tasks are planned for."""

    name: str
    species: str  # "dog" | "cat" | "other" (UML "animal")

    def eat(self) -> None:
        """Record/perform a feeding for this pet."""
        ...

    def sleep(self) -> None:
        """Record/perform a rest period for this pet."""
        ...


@dataclass
class Task:
    """A single care task (generalizes the UML "Walk").

    A walk is just one kind of task; feeding, meds, grooming, etc. are others.
    """

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"

    def schedule(self) -> None:
        """Mark this task as scheduled / place it on the plan."""
        ...

    def cancel(self) -> None:
        """Remove this task from the plan."""
        ...


@dataclass
class Owner:
    """The pet owner using PawPal+."""

    name: str
    experience: str = ""  # e.g. "beginner", "experienced"
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner (UML "ownsPet")."""
        ...


class Schedule:
    """Holds the day's tasks and produces an ordered daily plan."""

    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule."""
        ...

    def list_todays_tasks(self) -> list[Task]:
        """Return the tasks planned for today (UML "listTodaysTasks")."""
        ...

    def build_plan(self) -> list[Task]:
        """Order/select tasks into a daily plan based on constraints.

        Scheduling entry point — implemented in a later step.
        """
        ...
