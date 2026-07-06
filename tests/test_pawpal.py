from pawpal_system import Pet, Task


def test_task_completion():
    """mark_complete() flips a task's status from incomplete to complete."""
    task = Task("Morning walk", 30)
    assert task.done is False
    task.mark_complete()
    assert task.done is True


def test_task_addition():
    """Adding a task to a pet increases that pet's task count."""
    pet = Pet("Biscuit", "dog")
    assert len(pet.tasks) == 0
    task = Task("Feed", 10)
    pet.add_task(task)
    assert len(pet.tasks) == 1
    assert task.pet is pet
