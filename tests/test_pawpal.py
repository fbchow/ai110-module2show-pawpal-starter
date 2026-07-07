from datetime import date, timedelta

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task


def test_task_completion():
    """mark_complete() flips a task's status from incomplete to complete."""
    task = Task("Morning walk", 30)
    assert task.done is False
    task.mark_complete()
    assert task.done is True


def test_daily_task_recurs():
    """Completing a daily task spawns tomorrow's occurrence on the same pet."""
    pet = Pet("Biscuit", "dog")
    task = Task("Morning walk", 30, frequency=Frequency.DAILY)
    pet.add_task(task)

    task.mark_complete()

    assert len(pet.tasks) == 2
    assert task.done is True
    next_task = pet.tasks[1]
    assert next_task.done is False
    assert next_task.frequency is Frequency.DAILY
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_weekly_task_recurs():
    """Completing a weekly task spawns next week's occurrence."""
    pet = Pet("Mochi", "cat")
    task = Task("Grooming", 20, frequency=Frequency.WEEKLY)
    pet.add_task(task)

    task.mark_complete()

    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.done is False
    assert next_task.due_date == date.today() + timedelta(weeks=1)


def test_once_task_does_not_recur():
    """A one-off (default) task stays a single task after completion."""
    pet = Pet("Rex", "dog")
    task = Task("Vet visit", 45)
    pet.add_task(task)

    task.mark_complete()

    assert len(pet.tasks) == 1
    assert task.done is True


def test_task_addition():
    """Adding a task to a pet increases that pet's task count."""
    pet = Pet("Biscuit", "dog")
    assert len(pet.tasks) == 0
    task = Task("Feed", 10)
    pet.add_task(task)
    assert len(pet.tasks) == 1
    assert task.pet is pet


def test_filter_tasks():
    """filter_tasks narrows by completion status and by pet name."""
    biscuit = Pet("Biscuit", "dog")
    mittens = Pet("Mittens", "cat")

    walk = Task("Morning walk", 30)
    feed = Task("Feed", 10)
    groom = Task("Groom", 20)
    biscuit.add_task(walk)
    biscuit.add_task(feed)
    mittens.add_task(groom)

    walk.mark_complete()

    owner = Owner("Sam")
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    scheduler = Scheduler()

    # No filters -> every task.
    assert len(scheduler.filter_tasks(owner)) == 3

    # By completion status.
    assert scheduler.filter_tasks(owner, done=True) == [walk]
    assert scheduler.filter_tasks(owner, done=False) == [feed, groom]

    # By pet name (case-insensitive).
    assert scheduler.filter_tasks(owner, pet_name="biscuit") == [walk, feed]

    # Combined filters (AND).
    assert scheduler.filter_tasks(owner, done=False, pet_name="Biscuit") == [feed]
