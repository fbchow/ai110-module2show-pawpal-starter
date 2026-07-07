from datetime import date, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def _owner_with(*tasks, pet_name="Mochi", species="cat"):
    """Build an Owner with a single pet carrying the given tasks (in order)."""
    pet = Pet(pet_name, species)
    for t in tasks:
        pet.add_task(t)
    owner = Owner("Jordan")
    owner.add_pet(pet)
    return owner


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


# --- Sorting correctness ----------------------------------------------------


def test_sort_by_time_chronological():
    """H1: sort_by_time returns timed tasks in ascending clock order."""
    noon = Task("Lunch", 15, time="12:00")
    early = Task("Walk", 30, time="07:30")
    mid = Task("Play", 20, time="09:15")
    owner = _owner_with(noon, early, mid)  # added out of order

    assert Scheduler().sort_by_time(owner) == [early, mid, noon]


def test_sort_by_time_untimed_last():
    """E1: untimed tasks are pushed to the end, after all timed tasks."""
    untimed = Task("Cuddle", 10, time=None)
    timed = Task("Walk", 30, time="08:00")
    owner = _owner_with(untimed, timed)

    assert Scheduler().sort_by_time(owner) == [timed, untimed]


def test_sort_by_time_equal_times_stable():
    """E2: tasks sharing a time keep insertion order (stable sort, no crash)."""
    first = Task("Feed", 10, time="08:00")
    second = Task("Walk", 30, time="08:00")
    owner = _owner_with(first, second)

    assert Scheduler().sort_by_time(owner) == [first, second]


def test_tasks_by_priority_order():
    """H2: priority high-first, ties broken by shorter duration first."""
    low = Task("Nap", 15, priority=Priority.LOW)
    high_long = Task("Vet", 30, priority=Priority.HIGH)
    high_short = Task("Meds", 10, priority=Priority.HIGH)
    medium = Task("Groom", 20, priority=Priority.MEDIUM)
    owner = _owner_with(low, high_long, high_short, medium)

    # Both HIGH tasks first (shorter one leads), then MEDIUM, then LOW.
    assert Scheduler().tasks_by_priority(owner) == [high_short, high_long, medium, low]


# --- Recurrence logic (beyond the existing basics) --------------------------


def test_daily_recurrence_copies_time_slot():
    """E3: the spawned daily occurrence keeps the same time slot and is due tomorrow."""
    pet = Pet("Biscuit", "dog")
    task = Task("Walk", 30, time="08:00", frequency=Frequency.DAILY)
    pet.add_task(task)

    task.mark_complete()

    next_task = pet.tasks[1]
    assert next_task.time == "08:00"
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_recurrence_needs_pet():
    """E4: a daily task with no pet completes but spawns nothing (no crash)."""
    orphan = Task("Walk", 30, frequency=Frequency.DAILY)
    assert orphan.pet is None

    orphan.mark_complete()  # should not raise

    assert orphan.done is True


# --- Conflict detection -----------------------------------------------------


def test_no_conflict_distinct_times():
    """H3: tasks at different slots produce no conflict."""
    owner = _owner_with(
        Task("Walk", 30, time="08:00"),
        Task("Feed", 10, time="09:00"),
    )
    scheduler = Scheduler()

    assert scheduler.find_conflicts(owner) == []
    assert scheduler.has_conflicts(owner) is False


def test_conflict_same_time():
    """H4: two pending tasks at the same slot yield one naming warning."""
    owner = _owner_with(
        Task("Walk", 30, time="08:00"),
        Task("Feed", 10, time="08:00"),
    )
    conflicts = Scheduler().find_conflicts(owner)

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "Walk" in conflicts[0] and "Feed" in conflicts[0]


def test_conflict_ignores_untimed():
    """E5: untimed tasks occupy no slot and never conflict."""
    owner = _owner_with(
        Task("Cuddle", 10, time=None),
        Task("Nap", 20, time=None),
    )
    assert Scheduler().find_conflicts(owner) == []


def test_three_tasks_same_slot_one_warning():
    """E6: 3+ tasks in one slot collapse to a single warning for that slot."""
    owner = _owner_with(
        Task("Walk", 30, time="09:00"),
        Task("Feed", 10, time="09:00"),
        Task("Meds", 5, time="09:00"),
    )
    assert len(Scheduler().find_conflicts(owner)) == 1


def test_done_task_not_conflict():
    """E7: completed tasks free their slot, so they don't clash with the reopened one."""
    scheduler = Scheduler()

    # A done task sharing a slot with a pending one is not a conflict.
    done = Task("Old walk", 30, time="08:00", done=True)
    pending = Task("New walk", 30, time="08:00")
    owner = _owner_with(done, pending)
    assert scheduler.find_conflicts(owner) == []

    # Completing a daily timed task must not conflict with its fresh occurrence.
    pet = Pet("Biscuit", "dog")
    daily = Task("Walk", 30, time="08:00", frequency=Frequency.DAILY)
    pet.add_task(daily)
    flow_owner = Owner("Sam")
    flow_owner.add_pet(pet)
    daily.mark_complete()
    assert scheduler.find_conflicts(flow_owner) == []


# --- Edge cases spanning features -------------------------------------------


def test_empty_owner():
    """E8: an owner with no tasks (or no pets) yields empty results everywhere."""
    scheduler = Scheduler()

    for owner in (_owner_with(), Owner("Nobody")):  # pet-with-no-tasks, no-pets
        assert scheduler.sort_by_time(owner) == []
        assert scheduler.tasks_by_priority(owner) == []
        assert scheduler.find_conflicts(owner) == []
        assert scheduler.pending_tasks(owner) == []
        assert scheduler.build_plan(owner, 60) == []
        assert scheduler.has_conflicts(owner) is False


def test_build_plan_fits_budget():
    """H5: greedy plan takes the highest-priority tasks that fit the budget."""
    high = Task("Vet", 30, priority=Priority.HIGH)
    medium = Task("Groom", 30, priority=Priority.MEDIUM)
    low = Task("Nap", 30, priority=Priority.LOW)
    owner = _owner_with(high, medium, low)

    plan = Scheduler().build_plan(owner, available_minutes=60)

    assert plan == [high, medium]  # 60 min used; LOW dropped


def test_build_plan_skips_done():
    """E9: a completed task is never scheduled even if it fits the budget."""
    done = Task("Walk", 20, priority=Priority.HIGH, done=True)
    pending = Task("Feed", 10, priority=Priority.LOW)
    owner = _owner_with(done, pending)

    assert Scheduler().build_plan(owner, available_minutes=120) == [pending]
