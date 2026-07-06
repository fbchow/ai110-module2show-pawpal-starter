from pawpal_system import Owner, Pet, Task, Scheduler, Priority, format_plan

owner = Owner('Jordan')
dog = Pet('Biscuit', 'dog')
cat = Pet('Mochi', 'cat')
owner.add_pet(dog)
owner.add_pet(cat)
dog.add_task(Task('Morning walk', 30, Priority.HIGH, time='08:00'))
dog.add_task(Task('Vet visit', 45, Priority.LOW))
cat.add_task(Task('Feed cat', 10, Priority.HIGH, time='08:00'))

s = Scheduler()
print('todays_tasks:', [t.description for t in s.todays_tasks(owner)])
plan = s.build_plan(owner, 90)
print()
print(format_plan(plan))
print()
print('empty ->', repr(format_plan([])))