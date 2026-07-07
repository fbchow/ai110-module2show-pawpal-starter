from pawpal_system import Task, Pet, Owner, Scheduler, Priority, format_plan
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

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    pet.add_task(
        Task(
            description=task_title,
            duration_minutes=int(duration),
            priority=Priority[priority.upper()],  # "high" -> Priority.HIGH
        )
    )

tasks = owner.all_tasks()
if tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": t.description,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority.name,
                "done": t.done,
            }
            for t in tasks
        ]
    )
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
    st.text(format_plan(plan))
