from pawpal_system import Owner, Pet, Task, Scheduler, Priority, format_plan

# Test initial object creation
owner = Owner('Jordan')
dog = Pet('Biscuit', 'dog')
cat = Pet('Mochi', 'cat')
owner.add_pet(dog)
owner.add_pet(cat)
dog.add_task(Task('Morning walk', 30, Priority.HIGH, time='08:00'))
dog.add_task(Task('Vet visit', 45, Priority.LOW))
cat.add_task(Task('Feed cat', 10, Priority.HIGH, time='08:00'))
# Same-pet collision: dog already walks at 08:00, now also gets fed at 08:00.
dog.add_task(Task('Feed dog', 10, Priority.HIGH, time='08:00'))

# visualize a schedule in the terminal
s = Scheduler()
print('todays_tasks:', [t.description for t in s.todays_tasks(owner)])

# --- Conflict detection ----------------------------------------------------
# Morning walk (Biscuit) + Feed cat (Mochi) + Feed dog (Biscuit) all at 08:00.
print()
conflicts = s.find_conflicts(owner)
if conflicts:
    print('WARNING: schedule conflicts detected:')
    for warning in conflicts:
        print(f'  - {warning}')
else:
    print('No conflicts.')
print('=== ===')
plan = s.build_plan(owner, 90)
print()
print(format_plan(plan))
print()
print('empty ->', repr(format_plan([])))
print('=== ===')

# sort by time
o = Owner('Fanny')
p = Pet('Rex', 'dog')
o.add_pet(p)
p.add_task(Task('walk', 30, time='12:00'))
p.add_task(Task('feed', 10, time='08:30'))
p.add_task(Task('vet', 45, time=None))
print([(t.description, t.time) for t in Scheduler().sort_by_time(o)])
print('=== ===')

# --- Sorting + filtering demo ---------------------------------------------
# Tasks are added out of order (times and priorities scrambled) to prove the
# Scheduler's sort/filter methods reorder and select correctly.
demo = Owner('Alex')
rex = Pet('Rex', 'dog')
luna = Pet('Luna', 'cat')
demo.add_pet(rex)
demo.add_pet(luna)

rex.add_task(Task('Evening walk', 30, Priority.MEDIUM, time='18:00'))
rex.add_task(Task('Morning walk', 30, Priority.HIGH, time='07:00'))
luna.add_task(Task('Feed cat', 10, Priority.HIGH, time='12:30'))
rex.add_task(Task('Vet checkup', 45, Priority.LOW))            # untimed
luna.add_task(Task('Brush fur', 15, Priority.MEDIUM, time='09:15'))

sch = Scheduler()

# Mark one task complete so the done/not-done filters have something to split.
rex.tasks[1].mark_complete()  # Morning walk

print()
print('=== Scheduler demo (tasks added out of order) ===')

print('\nsort_by_time:')
for t in sch.sort_by_time(demo):
    print(f'  {t.time or "--:--"}  {t.description}')

print('\ntasks_by_priority:')
for t in sch.tasks_by_priority(demo):
    print(f'  [{t.priority.name}]  {t.description}')

print('\nfilter_tasks(done=True):')
print('  ', [t.description for t in sch.filter_tasks(demo, done=True)])

print('filter_tasks(done=False):')
print('  ', [t.description for t in sch.filter_tasks(demo, done=False)])

print("filter_tasks(pet_name='Luna'):")
print('  ', [t.description for t in sch.filter_tasks(demo, pet_name='Luna')])

print("filter_tasks(done=False, pet_name='Rex'):")
print('  ', [t.description for t in sch.filter_tasks(demo, done=False, pet_name='Rex')])