from pawpal_system import Task, Pet, Owner, Scheduler, Priority, Frequency, format_plan
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

# Streamlit re-runs this script top-to-bottom on every interaction, so plain
# local objects would be recreated empty each time. Store the domain objects in
# st.session_state (a dict that survives across re-runs) and create them once.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
owner = st.session_state.owner
scheduler = st.session_state.scheduler

# Keep the owner name in sync with the (editable) input on every run.
owner.name = owner_name

# Ensure the owner has a pet for tasks to attach to.
if not owner.pets:
    owner.add_pet(Pet(name=pet_name, species=species))
pet = owner.pets[0]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)
with col5:
    # Optional clock slot ("HH:MM"). Drives conflict detection in the Scheduler;
    # leave blank for an untimed task that occupies no slot.
    task_time = st.text_input("Time (HH:MM)", value="08:00")

if st.button("Add task"):
    pet.add_task(
        Task(
            description=task_title,
            duration_minutes=int(duration),
            priority=Priority[priority.upper()],  # "high" -> Priority.HIGH
            frequency=Frequency(frequency),       # "daily" -> Frequency.DAILY
            time=task_time.strip() or None,        # "08:00" -> scheduled slot
        )
    )

tasks = owner.all_tasks()
if tasks:
    # --- Sort & filter controls, powered by the Scheduler ---------------
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        sort_by = st.selectbox("Sort by", ["priority", "time"])
    with fcol2:
        status = st.selectbox("Show", ["all", "pending", "done"])

    # Filter first (by completion status), then sort the surviving tasks.
    done_filter = {"all": None, "pending": False, "done": True}[status]
    filtered = scheduler.filter_tasks(owner, done=done_filter)

    if sort_by == "priority":
        ordering = scheduler.tasks_by_priority(owner)
    else:
        ordering = scheduler.sort_by_time(owner)
    # Keep the chosen sort order but drop tasks removed by the filter.
    keep = set(id(t) for t in filtered)
    visible = [t for t in ordering if id(t) in keep]

    # --- Conflict warnings: surface BEFORE the table so they can't be
    #     scrolled past. One warning per clash, naming the exact slot and
    #     the colliding tasks so the owner knows what to reschedule. -----
    conflicts = scheduler.find_conflicts(owner)
    if conflicts:
        st.warning(
            f"⚠️ {len(conflicts)} scheduling conflict"
            f"{'s' if len(conflicts) > 1 else ''} — "
            "two tasks can't happen at the same time. "
            "Change one task's **Time (HH:MM)** to fix it."
        )
        for c in conflicts:
            st.warning(c)
    else:
        st.success("✅ No scheduling conflicts — every task has its own time slot.")

    st.write(f"Current tasks ({len(visible)} shown):")
    st.table(
        [
            {
                "time": t.time or "—",
                "title": t.description,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority.name,
                "frequency": t.frequency.value,
                "due_date": t.due_date.isoformat() if t.due_date else "—",
                "done": t.done,
            }
            for t in visible
        ]
    )

    # Completing a daily/weekly task auto-spawns its next occurrence.
    pending = scheduler.pending_tasks(owner)
    if pending:
        labels = {f"{t.description} ({t.frequency.value})": t for t in pending}
        choice = st.selectbox("Mark a task complete", list(labels))
        if st.button("Complete task"):
            labels[choice].mark_complete()
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Chooses and orders tasks by priority within your time budget.")

available_minutes = st.number_input(
    "Available minutes", min_value=1, max_value=1440, value=120
)

if st.button("Generate schedule"):
    plan = scheduler.build_plan(owner, available_minutes=int(available_minutes))
    if plan:
        total = sum(t.duration_minutes for t in plan)
        st.success(
            f"✅ Scheduled {len(plan)} task{'s' if len(plan) > 1 else ''} "
            f"using {total} of {int(available_minutes)} available minutes."
        )
        st.table(
            [
                {
                    "time": t.time or "—",
                    "title": t.description,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority.name,
                    "pet": t.pet.name if t.pet else "—",
                }
                for t in sorted(
                    plan, key=lambda t: (t.time is None, t.time or "", -t.priority)
                )
            ]
        )
        # A plan that fits the budget can still double-book a time slot.
        for c in scheduler.find_conflicts(owner):
            st.warning(c)
    else:
        st.info("No tasks fit the available time. Add tasks or increase the budget.")
